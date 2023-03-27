import os
import win32com.client
import config
import praw

#DELETE SSE SCHEDULED TASKS
def deletessetasks():
    folder_path = r"C:\Windows\System32\Tasks\SSE"

    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")
    task_folder = root_folder.GetFolder("SSE")

    for task in task_folder.GetTasks(0):
        # print(task.Name)
        task_folder.DeleteTask(task.Name, 0)

#DELETE MATCH THREAD SCHEDULED TASKS
def deletematchthreadtasks():
    folder_path = r"C:\Windows\System32\Tasks\MatchThreads"

    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")
    task_folder = root_folder.GetFolder("MatchThreads")

    for task in task_folder.GetTasks(0):
        # print(task.Name)
        task_folder.DeleteTask(task.Name, 0)

#DELETE AUTO-GENERATED SCRIPTS
def deletescripts():
    folder_path = config.directory+"SSEScripts"

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

    folder_path2 = config.directory+"SSEScripts\\MatchThreads"

    for filename in os.listdir(folder_path2):
        file_path = os.path.join(folder_path2, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

#DELETE DATABASE
def deletedb():
    file_path = config.directory+"botdatabase.db"

    os.remove(file_path)
    print(f"Deleted {file_path}")


try:
    deletescripts()
    deletedb()
    deletematchthreadtasks()
    deletessetasks()
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
    subject = "An error occurred in the post round cleanup"
    body = f"An error occurred:\n\n{e}"

    # Send message to recipient if an exception occurs
    reddit.redditor(recipient).message(subject, body)


