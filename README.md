# AFL Match Thread Bot

This is a Reddit bot for the AFL subreddit that posts match threads and a match thread index. The bot is implemented in Python and designed to run in Windows using Task Scheduler. Users of the code will need to use the config_template.py file with their own details, renamed to config.py.

<ins>Pre-install</ins>

Before you can use the AFL Match Thread Bot, you will need to obtain Reddit API credentials. Here's how to get them:

1. Go to https://www.reddit.com/prefs/apps and click the "Create App" or "Create Another App" button at the bottom of the page.
2. Select the "Script" option and give your app a name and description.
3. Set the "About url" and "Redirect uri" fields to any valid URL (e.g. http://localhost:8080).
4. Click "Create app" to create your app.
5. Your app's client ID and client secret will now be displayed on the app's information page. You will need to copy these values into your config.py file.

<ins>Installation</ins>

1. Clone this repository to your local machine.
2. Install the required Python packages by running pip install -r requirements.txt.
3. Rename config_template.py to config.py and fill in your Reddit API credentials and other details.

Here's how to add your credentials to the config.py file:

1. Open config.py in a text editor.
2. Enter your Reddit app's client ID and client secret in the client_id and client_secret fields, respectively.
3. Enter your Reddit username and password in the username and password fields, respectively.
4. Set the user_agent field to a unique string that describes your bot (e.g. myaflbot:v1.0).
5. Set the subreddit field to the name of the subreddit where you want to post match threads (e.g. afl).
6. Set the subredditurlbase field to the base URL of your subreddit's comment section (e.g. 'https://reddit.com/r/afl/comments/').
7. Set the messagerecipient field to the Reddit username of the recipient for error messages.
8. Set the directory field to the base directory of the code.
9. Once you have added your Reddit credentials to config.py, you will be able to use the AFL Match Thread Bot to create and manage match threads on the AFL subreddit.

<ins>How it Works</ins>

To run the AFL Match Thread Bot, you will need to schedule the following scripts to run on their respective days:

 - getrounddata.py should be scheduled to run on Wednesdays to retrieve the fixture data for the next round.
 - roundhubpost.py should be scheduled to run on Thursdays to create and post the match thread index for the current round. This also generates the scripts and scheduled tasks for each game's match thread + the script to manage a connection to the SSE game API
 - postroundcleanup.py should be scheduled to run on Tuesdays to remove auto-generated scripts and scheduled tasks
 
You can schedule these scripts to run automatically using Task Scheduler in Windows. Simply create a new task, set the trigger to run on the desired day and time, and set the action to run the Python interpreter with the path to the corresponding script as the argument.

Alternatively, you can manually run the scripts by executing the following commands in your terminal:
```
python getrounddata.py
python roundhubpost.py
python postroundcleanup.py
```

<ins>Contributing</ins>

I welcome contributions from anyone interested in improving the AFL Match Thread Bot. If you would like to contribute, please follow these steps:

1. Fork this repository.
2. Create a new branch for your changes.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request to this repository.
6. I will review your changes and merge them if they are deemed suitable. Please ensure that your code follows the existing code style and includes appropriate tests.

<ins>License</ins>
This project is licensed under the MIT License - see the LICENSE file for details.

<ins>Acknowledgements</ins>
This project was inspired by similar Reddit bots for other subreddits, and makes use of the praw Python package for interacting with the Reddit API. Also a huge thankyou to the person behind the squiggle API (https://api.squiggle.com.au/), this wouldn't be possible without their generosity re: hosting a free AFL API.
