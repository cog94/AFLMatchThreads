import json
import config
from datetime import datetime
import praw
import sqlite3


# format team names to match reddit format
def formatteamname(rawteamname):
    if rawteamname == "Greater Western Sydney":
        return "GWS Giants"
    elif rawteamname == "Brisbane Lions":
        return "Brisbane"
    else:
        return rawteamname

# format team names to match name of image in subreddit
def formatimagename(rawteamname):
    if rawteamname == "Greater Western Sydney":
        return "GWS"
    elif rawteamname == "Brisbane Lions":
        return "Brisbane"
    else:
        return rawteamname

# edit the round hub post for round with match thread urls
def redditsubmissionupdate():
   # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    conn.row_factory = sqlite3.Row  

    # Create a cursor
    cursor = conn.cursor()

    # Retrieve all data from the currentround table
    cursor.execute("SELECT * FROM currentround")
    rows = cursor.fetchall()

    huburl = (rows[0]['roundhuburl'])
    roundname = (rows[0]['roundname'])

    listmarkup = []

    for row in rows:
        #convert each row into dict object
        i = dict(row)

        # formatting date and timezone
        date = (i["date"])
        rawdate=  datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        # the API has vicbias, so the timezones default to melbourne (and the other eastern states who aren't scared of daylight savings) time. 
        if i["tz"] == "+11:00":
            tz = "AEDT"    
        else:
            tz = "AEST"

        formattedDate = rawdate.strftime("%A %d %b, %H:%M")

        # create google search url for converting to local time zones
        formattedTimeSearch = "https://www.google.com/search?q="+rawdate.strftime("%H")+"%3A"+rawdate.strftime("%M")+"+"+tz

        if i["matchthreadurl"] == None:
            line = "|^("+formattedDate+") ^["+tz+"]("+formattedTimeSearch+")|^("+formatteamname(i["hteam"])+") ^v ^("+formatteamname(i["ateam"])+")|^("+i["venue"]+")||||"
            listmarkup.append(line)
        elif i["postmatchurl"] == None:
            line = "|^("+formattedDate+") ^["+tz+"]("+formattedTimeSearch+")|^("+formatteamname(i["hteam"])+") ^v ^("+formatteamname(i["ateam"])+")|^("+i["venue"]+")|^[Link]("+ config.subredditurlbase +i["matchthreadurl"]+")||^>!"+str(i["hscore"])+"-"+str(i["ascore"])+"!<|"
            listmarkup.append(line)
        else:
            line = "|^("+formattedDate+") ^["+tz+"]("+formattedTimeSearch+")|^("+formatteamname(i["hteam"])+") ^v ^("+formatteamname(i["ateam"])+")|^("+i["venue"]+")|^[Link]("+ config.subredditurlbase +i["matchthreadurl"]+")|^[Link](" + config.subredditurlbase + i["postmatchurl"]+")|^>!"+str(i["hscore"])+"-"+str(i["ascore"])+"!<|"
            listmarkup.append(line)  
    
    conn.close()

    listmarkupstring = '\n'.join(str(x) for x in listmarkup)

    post_body="# Match Centre ("+str(roundname)+""")
|First Bounce|Fixture|Venue|MT|PMT|Score|
|:-|:--:|:--:|:-|:-|:--:|\n"""+listmarkupstring

    reddit = praw.Reddit(client_id = config.client_id,  
                         client_secret = config.client_secret,  
                         username = config.username,  
                         password = config.password, 
                         user_agent = config.user_agent) 

    submission = reddit.submission(url=config.subredditurlbase + str(huburl))
    submission.edit(body=post_body)

def updateroundhub(gamedata, url):

    id = gamedata["id"]

    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    cursor = conn.cursor()

    # Update matchthreadurl in database where id = gamedata["id"]
    cursor.execute('UPDATE currentround SET matchthreadurl=? WHERE id=?', (url, id))

    conn.commit()
    conn.close()

    redditsubmissionupdate()


def getURL(hometeam):
    # CONVERTING THE TEAM NAME FROM SQUIGGLE API TO MATCH AFL WEBSITE API DATA

    teamDict = {
        "Collingwood": "COLL",
        "Sydney": "SYD",
        "Greater Western Sydney": "GWS",
        "Adelaide": "ADEL",
        "Hawthorn": "HAW",
        "Melbourne": "MELB",
        "West Coast": "WCE",
        "Port Adelaide": "PORT",
        "Richmond": "RICH",
        "Fremantle": "FRE",
        "Geelong":  "GEEL",
        "Gold Coast":  "GCFC",
        "Essendon": "ESS",
        "Western Bulldogs": "WB" , 
        "North Melbourne": "NMFC" ,
        "Brisbane Lions": "BL" ,
        "Carlton": "CARL",
        "St Kilda": "STK", 
    }

    matchid_data_dict = {}

    #OPEN JSON FILE FOR CURRENT ROUND AFL WEBSITE DATA
    fa = open(config.directory+'afl_website_round_data.json')
    aflwebsitedata = json.load(fa)

    aflmatchdata = aflwebsitedata.get("matches")

    #FOR EACH MATCH, GRAB HOME TEAM ABBREVIATION AND MATCHID, STORE IN KEY-VALUE PAIR
    for i in aflmatchdata:
        matchid = i["id"]
        hometeamarray = i["home"].get("team")
        hometeamabbreviation = hometeamarray["abbreviation"]
        matchid_data_dict[hometeamabbreviation] = matchid

    fa.close()

    # GET ABBREVIATION OF SQUIGGLE DATA TEAM NAME, MATCH TO THE URL ID FROM AFL WEBSITE JSON. RETURN THE MATCH ID
    if hometeam in teamDict.keys():
        teamname = (teamDict.get(hometeam))
        # print(matchid_data_dict.get(teamname))
        return matchid_data_dict.get(teamname)

def createpost():
    gamedata = json.loads(data)
  
    # formatting date and timezone
    rawdate=  datetime.strptime(gamedata["date"], '%Y-%m-%d %H:%M:%S')

    # the API has vicbias, so the timezones default to melbourne (and the other eastern states who aren't scared of daylight savings) time. 
    if gamedata["tz"] == "+11:00":
        tz = "AEDT"    
    else:
        tz = "AEST"

    formattedDate = rawdate.strftime("%A %d %B")
    formattedTime = rawdate.strftime("%I:%M%p")

    # creating an authorized reddit instance 

    reddit = praw.Reddit(client_id = config.client_id,  
                         client_secret = config.client_secret,  
                         username = config.username,  
                         password = config.password, 
                         user_agent = config.user_agent) 


    # creating the post title and body
    post_title="Match Thread: "+ formatteamname(gamedata["hteam"]) + " vs "+ formatteamname(gamedata["ateam"])+" ("+gamedata["roundname"]+")"
    post_body="""
HOME TEAM | [](/empty) | AWAY TEAM
:--:|:--:|:--:
**"""+gamedata["hteam"]+"""** |  vs  | **"""+gamedata["ateam"]+"""** 
[](/"""+formatimagename(gamedata["hteam"]).lower().replace(" ","")+"""2) |    | [](/"""+formatimagename(gamedata["ateam"]).lower().replace(" ","")+"""2)

-----
INFORMATION | [](/empty)
    :--|:--
-----

**Date** |  """+formattedDate+"""

**Time** |  """+formattedTime+" "+tz+"""

**Ground** | """+gamedata["venue"]+"""

**Statistics** | [**AFL Match Centre**](https://www.afl.com.au/afl/matches/"""+str(getURL(gamedata["hteam"]))+""")

**Reddit Stream** | [**Stream**](https://reddit-stream.com/comments/auto)

**TV** | [**AFL Broadcast Guide Avaliable Here**](http://www.afl.com.au/broadcastguide)

Final teams available from the [**AFL Match Centre.**](https://www.afl.com.au/afl/matches/"""+str(getURL(gamedata["hteam"]))+""")

-----

As a reminder, the comment rules are listed in the sidebar. You are responsible for following the rules!

If you see a comment or post that breaks the rules, please report it to the moderators. This helps keep the subreddit clear of rule-breaking content. 

If you want to make **any** comment on the umpiring *only*, the comment must be a rhyme or limerick while also in line with the subreddits rules. No abuse. No snide swipes at an individual, do not be a dickhead, any comments not doing this will be removed.

See any antisocial behaviour? Please report dickhead comments around you using the report button.

Antisocial behaviour can result in your removal from the Match Thread (1 day ban).
    
    """

    # submitting post to subreddit, return the post id
    matchthreadurl = reddit.subreddit(config.subreddit).submit(title=post_title, selftext=post_body)
    
    if matchthreadurl:
        updateroundhub(gamedata, str(matchthreadurl))
    

try:
    createpost()
except Exception as e:
    print(e)
    id = gamedata["id"]

    # Set up Reddit API credentials
    reddit = praw.Reddit(
        client_id = config.client_id,  
        client_secret = config.client_secret,  
        username = config.username,  
        password = config.password, 
        user_agent = config.user_agent
    ) 
    
    # Set up recipient username and message subject and body
    recipient =  config.messagerecipient
    subject = "An error occurred in creating the match thread for "+id
    body = f"An error occurred:\n\n{e}"

    # Send message to recipient if an exception occurs
    reddit.redditor(recipient).message(subject, body)
