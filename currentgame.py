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


# Define a function to handle a score, and updating the json file
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
                result += ". [HOIST IT](https://gfycat.com/diligentcooleasternnewt)"
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

**Result** | >!"""+formatresult(gamedata)+"""!<

**Date** |  """+formattedDate+"""

**Time** |  """+formattedTime+" "+tz+"""

**Ground** | """+gamedata["venue"]+"""

-----
    
    """

    # submitting post to subreddit, return the post id
    postmatchurl = reddit.subreddit(config.subreddit).submit(title=post_title, selftext=post_body)
    
    if postmatchurl:
        updateroundhub(str(postmatchurl))


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
                gamefinished()
                # Break the loop and disconnect
                break

            # Check if the event type is a score
            if event.event == "score":
                print("They scored, time to update reddit post")
                homescore = str(data["score"]["hscore"])
                homegoals = str(data["score"]["hgoals"])
                homebehinds = str(data["score"]["hbehinds"])
                awayscore = str(data["score"]["ascore"])
                awaygoals = str(data["score"]["agoals"])
                awaybehinds = str(data["score"]["abehinds"])
                updateroundhubscores(homescore, awayscore, homegoals, homebehinds, awaygoals, awaybehinds )

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