import config
from datetime import datetime, timedelta
import praw
import sqlite3
import shutil
import os
import json

# format team names to match reddit format
def formatteamname(rawteamname):
    if rawteamname == "Greater Western Sydney":
        return "GWS Giants"
    elif rawteamname == "Brisbane Lions":
        return "Brisbane"
    else:
        return rawteamname


def createandschedulematchthreadscript(huburl):
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    conn.row_factory = sqlite3.Row  

    # Create a cursor
    cursor = conn.cursor()

    # Retrieve all data from the currentround table
    cursor.execute("SELECT * FROM currentround")
    rows = cursor.fetchall()

    # Copy the file named "config.py" to the new directory
    shutil.copy2(config.directory + '/config.py', config.directory + '/SSEScripts/MatchThreads')

    for row in rows:
        gamedata = dict(row)
        scriptname = gamedata["id"]
        gametime = gamedata["date"]
        rawdate=  datetime.strptime(gametime, '%Y-%m-%d %H:%M:%S')

        # Subtract 1 hour from rawdate using datetime.timedelta
        one_hour = timedelta(hours=1)
        new_datetime = rawdate - one_hour

        # starttime = new_datetime.strftime("%H:%M")
        start_date = new_datetime.strftime('%d/%m/%Y')
        start_time = new_datetime.strftime('%H:%M')

        # Copy the file named "currentgame.py" to the new directory
        shutil.copy2(config.directory + '/matchthreadpost.py', config.directory + '/SSEScripts/MatchThreads')

        # Rename the copied file to match the game ID
        os.rename(config.directory + '/SSEScripts/MatchThreads/matchthreadpost.py', config.directory + 'SSEScripts/MatchThreads/'+str(scriptname)+'.py')

        with open(config.directory +'/SSEScripts/MatchThreads/'+str(scriptname)+'.py', 'r') as f:
            lines = f.readlines()

            # Insert the gamedata to the script
            lines.insert(8, "data = '"+json.dumps(gamedata)+"'\n")
            lines.insert(9, "huburl = '"+huburl+"'\n")

            # Open the file named in write mode
            with open(config.directory +'/SSEScripts/MatchThreads/'+str(scriptname)+'.py', 'w') as f:
                # Write all the lines of the list back to the file
                f.writelines(lines)
        f.close()

        # Get the path of the script
        script_path = config.directory +'\\SSEScripts\\MatchThreads\\'+str(scriptname)+'.py'
        # print(script_path)

        # Create a command to run the game.py script using the python interpreter
        command = f"cmd /c python -i '{script_path}'"
        # print(command)

        # Create a task name for scheduling
        task_name = str(scriptname)+'matchthread.py'

        # Create a command to schedule the task using schtasks.exe
        task_command = f'schtasks /create /tn "MatchThreads\\{task_name}" /tr "{command}" /sc once /sd "{start_date}" /st "{start_time}'

        # # Set the folder name where the task will be created
        # folder_name = "MatchThreads"

        # # Create the full path to the folder
        # folder_path = f"C:\\Windows\\System32\\Tasks\\{folder_name}"

        # # Create the command to create the task inside the folder
        # task_command = f'schtasks /create /tn {folder_path}\\{task_name} /tr "{command}" /sc once /st {starttime}'

        # Run the task command using os.system()
        os.system(task_command)


    cursor.close()
    conn.close()


def createandscheduleSSEscript():
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    conn.row_factory = sqlite3.Row  

    # Create a cursor
    cursor = conn.cursor()

    # Retrieve all data from the currentround table
    cursor.execute("SELECT * FROM currentround")
    rows = cursor.fetchall()

    # Copy the file named "config.py" to the new directory
    shutil.copy2(config.directory + '/config.py', config.directory + '/SSEScripts/')

    for row in rows:
        gamedata = dict(row)

        scriptname = gamedata["id"]
        gametime = gamedata["date"]
        rawdate=  datetime.strptime(gametime, '%Y-%m-%d %H:%M:%S')
        start_date = rawdate.strftime('%d/%m/%Y')
        start_time = rawdate.strftime('%H:%M')

        # Copy the file named "currentgame.py" to the new directory
        shutil.copy2(config.directory + '/currentgame.py', config.directory + '/SSEScripts')

        # Rename the copied file to match the game ID
        os.rename(config.directory + '/SSEScripts/currentgame.py', config.directory + '/SSEScripts/'+str(scriptname)+'.py')

        with open(config.directory +'/SSEScripts/'+str(scriptname)+'.py', 'r') as f:
            lines = f.readlines()

            # Insert the line "gameid = id" at the thirteenth position (index 12) of the list
            lines.insert(12, "gameid = '"+str(scriptname)+"'\n")

            # Open the file named in write mode
            with open(config.directory +'/SSEScripts/'+str(scriptname)+'.py', 'w') as f:
                # Write all the lines of the list back to the file
                f.writelines(lines)

        
        # Get the path of the game.py script
        script_path = config.directory +'\\SSEScripts\\'+str(scriptname)+'.py'
        # print(script_path)

        # Create a command to run the game.py script using the python interpreter
        command = f"cmd /c python -i '{script_path}'"
        # print(command)

        # Create a task name for scheduling
        task_name = str(scriptname)+'.py'

        # Create a command to schedule the task using schtasks.exe
        schedule_command = f'schtasks /create /tn "SSE\\{task_name}" /tr "{command}" /sc once /sd "{start_date}" /st "{start_time}'

        # Run the schedule command using os.system()
        os.system(schedule_command)

    cursor.close()
    conn.close()


def updatedatabase(huburl):
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    cursor = conn.cursor()

    # Check if the columns exist in the table
    cursor.execute("PRAGMA table_info(currentround)")
    columns = cursor.fetchall()

    if not any(column[1] == 'roundhuburl' for column in columns):
        # Add roundhuburl column
        cursor.execute("ALTER TABLE currentround ADD COLUMN roundhuburl TEXT")

    if not any(column[1] == 'matchthreadurl' for column in columns):
        # Add matchthreadurl column
        cursor.execute("ALTER TABLE currentround ADD COLUMN matchthreadurl TEXT")

    if not any(column[1] == 'postmatchurl' for column in columns):
        # Add postmatchurl column
        cursor.execute("ALTER TABLE currentround ADD COLUMN postmatchurl TEXT")
    
    # Add the hub url to each row in the currentround table
    cursor.execute("UPDATE currentround SET roundhuburl = ?", (huburl,))
    
    # Commit the changes
    conn.commit()

    # Close the cursor and the connection
    cursor.close()
    conn.close()


def createpost():
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')
    conn.row_factory = sqlite3.Row  

    # Create a cursor
    cursor = conn.cursor()

    # Retrieve all data from the currentround table
    cursor.execute("SELECT * FROM currentround ORDER BY datetime(strftime('%Y-%m-%d %H:%M:%S', date)) ASC")
    rows = cursor.fetchall()

    # Get the round number 
    roundname = (rows[0]["roundname"])

    # formatting this weeks games into reddit markup for the post
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

        line = "|^("+formattedDate+") ^["+tz+"]("+formattedTimeSearch+")|^("+formatteamname(i["hteam"])+") ^v ^("+formatteamname(i["ateam"])+")|^("+i["venue"]+")||||"
        listmarkup.append(line)   

    listmarkupstring = '\n'.join(str(x) for x in listmarkup)

    conn.close()

    # creating an authorized reddit instance 
    # print("Logging in....")
    reddit = praw.Reddit(client_id = config.client_id,  
                        client_secret = config.client_secret,  
                        username = config.username,  
                        password = config.password, 
                        user_agent = config.user_agent) 
    # print("Logged in!")

    # creating the post title and body
    post_title="Match Threads: "+str(roundname)
    post_body="# Match Centre ("+str(roundname)+""")
|First Bounce|Fixture|Venue|MT|PMT|Score|
|:-|:--:|:--:|:-|:-|:-|\n"""+listmarkupstring

    huburl = reddit.subreddit(config.subreddit).submit(title=post_title, selftext=post_body)

    updatedatabase(str(huburl))
    createandschedulematchthreadscript(str(huburl))
    createandscheduleSSEscript()

try:
    createpost()
except Exception as e:
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
    subject = "An error occurred in the round hub post"
    body = f"An error occurred:\n\n{e}"

    # Send message to recipient if an exception occurs
    reddit.redditor(recipient).message(subject, body)
