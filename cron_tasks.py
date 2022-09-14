""" Completes cron tasks from Heroku Scheduler. """
import os
# import time
import datetime
import psycopg2
import psycopg2.extras
# import requests

from dotenv import load_dotenv
load_dotenv()

# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

now = datetime.datetime.now()
print(f"Running cron_tasks.py at {now}...")
print(now.strftime("%H:%M:%S:%w"))
current_time = {
    "day":now.strftime("%w"),
    "hour":now.strftime("%H"),
    "minute":now.strftime("%H"),
}
print(current_time)

def reminders_fetch():
    """ Checks for scheduled tasks. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            # Download file by id, structure metadata
            cur.execute("SELECT * FROM reminder_schedule")
            data = cur.fetchall()
            cur.close()
            print(f"Recurring reminders fetched!")

            reminders = []
            for row in data:
                reminders.append(dict(row._asdict()))

            # for key, val in data:
            #     reminder = {}
            #     reminders.append(reminder)
            #     reminder[key] = val
            # for d in data:
            #     print(d.reminder_id, d.day, d.hour, d.minute, d.reminded)
            #     reminders.reminder_id = d.reminder_id
            #     reminders.day = d.day
            #     reminders.hour = d.hour
            #     reminders.minute
                # print(f"{d['reminder_id']} {d['day']} {d['hour']} {d['minute']} {d['reminded']}")
            
            print("reminders:")
            for reminder in reminders:
                print(reminder.values())

    conn.close()

    return reminders

def reminders_queue():
    print("todo")

def main():
    """ Runs scheduled functions. """
    try:
        reminders = reminders_fetch()
        # queue = reminders_queue(reminders)
        # reminders_send(queue)

    except Exception as e:
        print(f"Error!: {e}")

    # content = "foo"
    # r = requests.get('https://www.turkosaur.us/ping/%s' % content)
    # print(r)

if __name__ == '__main__':
    main()
