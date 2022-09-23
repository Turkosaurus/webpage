""" Completes cron tasks from Heroku Scheduler. """
import os
import datetime
from dotenv import load_dotenv
from reminders import get_reminders, send_reminders

load_dotenv()
# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

now = datetime.datetime.now()
print(f"Running cron_tasks.py at {now}...")

def main():
    """ Runs scheduled functions. """
    try:
        send_reminders(get_reminders())

    except Exception as error:
        print(f"Error: {error}")

    # content = "foo"
    # r = requests.get('https://www.turkosaur.us/ping/%s' % content)
    # print(r)

if __name__ == '__main__':
    main()
