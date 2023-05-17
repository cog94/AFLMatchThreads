# Import modules
import requests
import sseclient
import json
import sqlite3
import config
from datetime import datetime
import praw 

# Define API url
api_url = "https://api.squiggle.com.au/sse/events/"


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


# edit the match thread with the post match thread url
def redditmatchthreadupdate(gamedata, postmatchurl):
    matchthreadurl = gamedata['matchthreadurl']

    # Format the date and timezone
    date = gamedata['date']
    rawdate = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    # the API has vicbias, so the timezones default to melbourne (and the other eastern states who aren't scared of daylight savings) time. 
    if gamedata["tz"] == "+11:00":
        tz = "AEDT"    
    else:
        tz = "AEST"

    formattedDate = rawdate.strftime("%A %d %B")
    formattedTime = rawdate.strftime("%I:%M%p")

    if gamedata['tz'] == "+11:00":
        tz = "AEDT"    
    else:
        tz = "AEST"

    formattedDate = rawdate.strftime("%A %d %b, %H:%M")

 # creating the post body
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

**Post Match Thread** |  [**Link**]("""+config.subredditurlbase +str(postmatchurl)+""")

**Match Thread Hub** |  [**Link**]("""+config.subredditurlbase +str(gamedata["roundhuburl"])+""")

-----

As a reminder, the comment rules are listed in the sidebar. You are responsible for following the rules!

If you see a comment or post that breaks the rules, please report it to the moderators. This helps keep the subreddit clear of rule-breaking content. 

If you want to make **any** comment on the umpiring *only*, the comment must be a rhyme or limerick while also in line with the subreddits rules. No abuse. No snide swipes at an individual, do not be a dickhead, any comments not doing this will be removed.

See any antisocial behaviour? Please report dickhead comments around you using the report button.

Antisocial behaviour can result in your removal from the Match Thread (1 day ban).
    
    """


    reddit = praw.Reddit(client_id = config.client_id,  
                         client_secret = config.client_secret,  
                         username = config.username,  
                         password = config.password, 
                         user_agent = config.user_agent) 

    submission = reddit.submission(url=config.subredditurlbase + str(matchthreadurl))
    submission.edit(body=post_body)

# edit the round hub post for round with match thread urls
def redditsubmissionupdate():
   # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    conn.row_factory = sqlite3.Row  

    # Create a cursor
    cursor = conn.cursor()

    # Retrieve all data from the currentround table
    cursor.execute("SELECT * FROM currentround ORDER BY datetime(strftime('%Y-%m-%d %H:%M:%S', date)) ASC")
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


# Update database scores, and then update the reddit post
def updateroundhubscores(homescore, awayscore, homegoals, homebehinds, awaygoals, awaybehinds ):
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    cursor = conn.cursor()

    # Update database where id = gameid
    cursor.execute('UPDATE currentround SET hscore=? WHERE id=?', (homescore, gameid))
    cursor.execute('UPDATE currentround SET ascore=? WHERE id=?', (awayscore, gameid))
    cursor.execute('UPDATE currentround SET hgoals=? WHERE id=?', (homegoals, gameid))
    cursor.execute('UPDATE currentround SET hbehinds=? WHERE id=?', (homebehinds, gameid))
    cursor.execute('UPDATE currentround SET agoals=? WHERE id=?', (awaygoals, gameid))
    cursor.execute('UPDATE currentround SET abehinds=? WHERE id=?', (awaybehinds, gameid))

    conn.commit()
    conn.close()

    redditsubmissionupdate()

# Update database scores 
def updatedatabasescores(homescore, awayscore, homegoals, homebehinds, awaygoals, awaybehinds ):
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    cursor = conn.cursor()

    # Update database where id = gameid
    cursor.execute('UPDATE currentround SET hscore=? WHERE id=?', (homescore, gameid))
    cursor.execute('UPDATE currentround SET ascore=? WHERE id=?', (awayscore, gameid))
    cursor.execute('UPDATE currentround SET hgoals=? WHERE id=?', (homegoals, gameid))
    cursor.execute('UPDATE currentround SET hbehinds=? WHERE id=?', (homebehinds, gameid))
    cursor.execute('UPDATE currentround SET agoals=? WHERE id=?', (awaygoals, gameid))
    cursor.execute('UPDATE currentround SET abehinds=? WHERE id=?', (awaybehinds, gameid))

    conn.commit()
    conn.close()


def formatresult(gamedata):
    hometeam = formatteamname(gamedata["hteam"])
    homescore = int(gamedata["hscore"]) 
    homegoals = gamedata["hgoals"] 
    homebehinds = gamedata["hbehinds"] 
    awayteam = formatteamname(gamedata["ateam"])
    awayscore = int(gamedata["ascore"])
    awaygoals = gamedata["agoals"] 
    awaybehinds = gamedata["abehinds"] 

    result = ""
    if homescore > awayscore:
            result += hometeam + " (" +str(homegoals) +"." + str(homebehinds) + "." + str(homescore) +") defeated " + awayteam + " (" + str(awaygoals) + "." + str(awaybehinds) + "." + str(awayscore) + ")"
    elif homescore < awayscore:
            result += hometeam + " (" +str(homegoals) +"." + str(homebehinds) + "." + str(homescore) +") was defeated by " + awayteam + " (" + str(awaygoals) + "." + str(awaybehinds) + "." + str(awayscore) + ")"
    else:
            result += hometeam + " (" +str(homegoals) +"." + str(homebehinds) + "." + str(homescore) +") drew with " + awayteam + " (" + str(awaygoals) + "." + str(awaybehinds) + "." + str(awayscore) + ")"

    if hometeam == "Essendon" or awayteam == "Essendon":
        if hometeam == "Essendon" and homescore > awayscore or awayteam == "Essendon" and awayscore > homescore:
            result += ". [HOIST IT, DILIGENTLY](https://gfycat.com/diligentcooleasternnewt)"

    if hometeam == "Collingwood" or awayteam == "Collingwood":
        if hometeam == "Collingwood" and homescore > awayscore or awayteam == "Collingwood" and awayscore > homescore:
            result += ". [HOIST IT | COLLINGWOOD VERSION, GONE WILD](https://gfycat.com/sameradianticelandichorse)"

    if hometeam == "Geelong" or awayteam == "Geelong":
        if hometeam == "Geelong" and homescore > awayscore or awayteam == "Geelong" and awayscore > homescore:
            result += ". [GEELONG_WIN.GIF](https://imgur.com/Fwu3Rl8)"

    if hometeam == "Greater Western Sydney" or awayteam == "Greater Western Sydney":
        if hometeam == "Greater Western Sydney" and homescore > awayscore or awayteam == "Greater Western Sydney" and awayscore > homescore:
            result += ". [GWS_DANCE.MP4](https://www.youtube.com/watch?v=QQjSP0eKytw)"

    if hometeam == "Fremantle" or awayteam == "Fremantle":
        if hometeam == "Fremantle" and homescore > awayscore or awayteam == "Fremantle" and awayscore > homescore:
            result += ". [FOREVER_FREO.GIF](https://gfycat.com/heavykindhoneycreeper)"

    if hometeam == "Sydney" or awayteam == "Sydney":
        if hometeam == "Sydney" and homescore > awayscore or awayteam == "Sydney" and awayscore > homescore:
            result += ". [PARKER.GIF](https://gfycat.com/genuineweeamurratsnake)"

    if hometeam == "Adelaide" or awayteam == "Adelaide":
        if hometeam == "Adelaide" and homescore > awayscore or awayteam == "Adelaide" and awayscore > homescore:
            result += ". [THUMBS_UP.PNG](https://imgur.com/2rDeGvp)"

    return result

    # if homescore > awayscore:
    #     return hometeam + " (" +str(homegoals) +"." + str(homebehinds) + "." + str(homescore) +") defeated " + awayteam + " (" + str(awaygoals) + "." + str(awaybehinds) + "." + str(awayscore) + ")"
    # elif homescore < awayscore:
    #     return hometeam + " (" +str(homegoals) +"." + str(homebehinds) + "." + str(homescore) +") was defeated by " + awayteam + " (" + str(awaygoals) + "." + str(awaybehinds) + "." + str(awayscore) + ")"
    # else:
    #     return hometeam + " (" +str(homegoals) +"." + str(homebehinds) + "." + str(homescore) +") drew with " + awayteam + " (" + str(awaygoals) + "." + str(awaybehinds) + "." + str(awayscore) + ")"

def updateroundhub(url):
     # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    cursor = conn.cursor()

    # Update postmatchurl in database where id = gameid
    cursor.execute('UPDATE currentround SET postmatchurl=? WHERE id=?', (url, gameid))

    conn.commit()
    conn.close()

    redditsubmissionupdate()

# post match thread to subreddit
def makepostmatch(gamedata):
    
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
    post_title="Post Match Thread: "+ formatteamname(gamedata["hteam"]) + " vs "+ formatteamname(gamedata["ateam"])+" ("+gamedata["roundname"]+")"
    post_body="""
HOME TEAM | [](/empty) | AWAY TEAM
:--:|:--:|:--:
**"""+gamedata["hteam"]+"""** |  vs  | **"""+gamedata["ateam"]+"""** 
[](/"""+formatimagename(gamedata["hteam"]).lower().replace(" ","")+"""2) |    | [](/"""+formatimagename(gamedata["ateam"]).lower().replace(" ","")+"""2)

-----
INFORMATION | [](/empty)
    :--|:--
-----

**Result** | """+formatresult(gamedata)+"""

**Date** |  """+formattedDate+"""

**Time** |  """+formattedTime+" "+tz+"""

**Ground** | """+gamedata["venue"]+"""

-----

**Match Thread** |  [**Link**]("""+config.subredditurlbase +gamedata["matchthreadurl"]+""")

**Match Thread Hub** |  [**Link**]("""+config.subredditurlbase +gamedata["roundhuburl"]+""")

-----
    
    """

    # submitting post to subreddit, return the post id
    postmatchurl = reddit.subreddit(config.subreddit).submit(title=post_title, selftext=post_body)
    
    if postmatchurl:
        updateroundhub(str(postmatchurl))
        redditmatchthreadupdate(gamedata, str(postmatchurl))  


def gamefinished():
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    conn.row_factory = sqlite3.Row  

    # Create a cursor
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM currentround WHERE id = ?", (gameid,)) 

    row = cursor.fetchone()

    makepostmatch(dict(row)) 
            

# Define a function to handle SSE
def handle_sse():
    # Create a sseclient object from the response
    client = sseclient.SSEClient(api_url+str(gameid))

    # Loop through the SSE events
    for event in client:
        # Parse the event data as json

        if(event.data):
            data = json.loads(event.data)

            # Check if the event type is winner
            if event.event == "winner":
                print("Game over man. Game over")
                gamefinished()
                # Break the loop and disconnect
                break

            # Check if the event type is a score
            if event.event == "score":
                print("They scored")
                scoretype = str(data["type"])
                homescore = str(data["score"]["hscore"])
                homegoals = str(data["score"]["hgoals"])
                homebehinds = str(data["score"]["hbehinds"])
                awayscore = str(data["score"]["ascore"])
                awaygoals = str(data["score"]["agoals"])
                awaybehinds = str(data["score"]["abehinds"])

                if scoretype == "goal":
                    print("It was a goal, so it's time to edit the database and round hub")
                    updateroundhubscores(homescore, awayscore, homegoals, homebehinds, awaygoals, awaybehinds )

                if scoretype == "behind":
                    print("It was a behind, so we'll only update the database")
                    updatedatabasescores(homescore, awayscore, homegoals, homebehinds, awaygoals, awaybehinds )
              

# Try to handle SSE
try:
    handle_sse()

# Except any connection errors
except requests.exceptions.ConnectionError as e:
    # Print the error message
    print(e)

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
    subject = "An error occurred in the SSE for "+gameid
    body = f"An error occurred:\n\n{e}"

    # Send message to recipient if an exception occurs
    reddit.redditor(recipient).message(subject, body)

    # Reconnect and handle SSE again
    handle_sse()