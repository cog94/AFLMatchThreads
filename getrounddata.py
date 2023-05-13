import json
import requests
import datetime 
import config
import praw
import sqlite3

def getaflwebsitedata(roundnumber):
    # Get current year
    today = datetime.date.today()
    year = today.year

    # Convert year to AFL season number
    seasonnumber = year - 1971 

    # API URL
    url = 'https://aflapi.afl.com.au/afl/v2/matches?competitionId=1&compSeasonId='+str(seasonnumber)+'&pageSize=50&roundNumber='+str(roundnumber)

    # Make request to API
    aflwebsitedata = requests.get(url=url)

    # SERIALISE JSON FOR OUTPUT TO FILE
    json_object = json.dumps(aflwebsitedata.json(), indent=4)

    # IF API REQUEST SUCCESFUL, WRITE THE JSON DATA TO FILE
    if aflwebsitedata.status_code == 200:
        f = open(config.directory+"afl_website_round_data.json", "w")
        f.write(json_object)
        f.close()
    else:
        print("Error. Status Code:"+str(aflwebsitedata.status_code))

def getcurrentroundfromdb():
    # Connect to the database
    conn = sqlite3.connect(config.directory + 'botdatabase.db')

    # Create a cursor
    cursor = conn.cursor()

    # Get the current date
    current_date = datetime.datetime.now()

    # Get the date 7 days from now
    week_from_now = current_date + datetime.timedelta(days=7)

    # Execute the query
    # cursor.execute("SELECT * FROM fixture WHERE date < ?", (week_from_now.strftime('%Y-%m-%d %H:%M:%S'),))
    cursor.execute("SELECT * FROM fixture WHERE date >= ? AND date < ? ORDER BY datetime(strftime('%Y-%m-%d %H:%M:%S', localtime)) ASC", (current_date.strftime('%Y-%m-%d %H:%M:%S'), week_from_now.strftime('%Y-%m-%d %H:%M:%S')))
     
    # Fetch the results
    results = cursor.fetchall()

    # Get the round number 
    roundnumber = (results[0][17])
    # print('Round number is '+str(roundnumber))

    # Create the "currentround" table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS currentround
                (id INTEGER PRIMARY KEY,
                complete INTEGER,
                year INTEGER,
                winnerteamid INTEGER,
                timestr TEXT,
                localtime TEXT,
                tz TEXT,
                hscore INTEGER,
                hbehinds INTEGER,
                is_final INTEGER,
                agoals INTEGER,
                abehinds INTEGER,
                hgoals INTEGER,
                ascore INTEGER,
                hteam TEXT,
                hteamid INTEGER,
                unixtime INTEGER,
                round INTEGER,
                ateamid INTEGER,
                ateam TEXT,
                updated TEXT,
                winner TEXT,
                venue TEXT,
                roundname TEXT,
                date TEXT,
                is_grand_final INTEGER)''')

    # Insert the results into the "currentround" table
    for row in results:
        print(row[0])
        cursor.execute('''INSERT INTO currentround (id, complete, year, winnerteamid, timestr, localtime, tz, hscore, hbehinds, is_final, agoals, abehinds, hgoals, ascore, hteam, hteamid, unixtime, round, ateamid, ateam, updated, winner, venue, roundname, date, is_grand_final)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25]))

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    getaflwebsitedata(roundnumber)

def getFixtureData():
    # API URL AND USER-AGENT
    url = 'https://api.squiggle.com.au/?q=games;year='

    headers = {
    'User-Agent': 'Reddit bot for r/AFL. Please message u/cog_94 with any concerns'
    }

    # GET CURRENT YEAR FOR API REQUST
    today = datetime.date.today()
    year = today.year

    # GET ALL GAMES FROM CURRENT YEAR
    fixture = requests.get(url+str(year), headers=headers)
    json_data = fixture.json()

    if fixture.status_code == 200:
        # Sort the data by earliest to latest localtime (datetime)
        sorted_data = sorted(json_data['games'], key=lambda x: x['localtime'])

         # Connect to the database
        conn = sqlite3.connect(config.directory + 'botdatabase.db')

        # Create a cursor
        cursor = conn.cursor()

        # Create the table
        cursor.execute('''CREATE TABLE IF NOT EXISTS fixture
                    (id INTEGER PRIMARY KEY,
                    complete INTEGER,
                    year INTEGER,
                    winnerteamid INTEGER,
                    timestr TEXT,
                    localtime TEXT,
                    tz TEXT,
                    hscore INTEGER,
                    hbehinds INTEGER,
                    is_final INTEGER,
                    agoals INTEGER,
                    abehinds INTEGER,
                    hgoals INTEGER,
                    ascore INTEGER,
                    hteam TEXT,
                    hteamid INTEGER,
                    unixtime INTEGER,
                    round INTEGER,
                    ateamid INTEGER,
                    ateam TEXT,
                    updated TEXT,
                    winner TEXT,
                    venue TEXT,
                    roundname TEXT,
                    date TEXT,
                    is_grand_final INTEGER)''')

        for game in sorted_data:
            cursor.execute('''INSERT INTO fixture (complete, year, winnerteamid, timestr, localtime, tz, id, hscore, hbehinds, is_final, agoals, abehinds, hgoals, ascore, hteam, hteamid, unixtime, round, ateamid, ateam, updated, winner, venue, roundname, date, is_grand_final)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (game['complete'], game['year'], game['winnerteamid'], game['timestr'], game['localtime'], game['tz'], game['id'], game['hscore'], game['hbehinds'], game['is_final'], game['agoals'], game['abehinds'], game['hgoals'], game['ascore'], game['hteam'], game['hteamid'], game['unixtime'], game['round'], game['ateamid'], game['ateam'], game['updated'], game['winner'], game['venue'], game['roundname'], game['date'], game['is_grand_final']))

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()

    else:
        print("Error. Status Code:"+str(fixture.status_code))

try:
    getFixtureData()
    getcurrentroundfromdb()
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
    subject = "An error occurred in the getting round data"
    body = f"An error occurred:\n\n{e}"

    # Send message to recipient if an exception occurs
    reddit.redditor(recipient).message(subject, body)

