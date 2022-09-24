""" Reminders functions """
import os
import time
import datetime
from datetime import timedelta
import psycopg2.extras
from dotenv import load_dotenv
# from application import send_msg

# PostgreSQL database connection
load_dotenv()
db = os.getenv('DATABASE_URL')

def get_reminders():
    """ Retrieves all reminders from database. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            now = datetime.datetime.now()
            cur.execute("SELECT * FROM reminders_schedule \
                WHERE day=%s AND active=True", (now.strftime("%w"),))
            data = cur.fetchall()

            batch_start = time.perf_counter()

            reminders = []
            for row in data:

                # convert generic weekly reminder to specifically this week
                due = datetime.datetime(
                    int(now.strftime("%Y")), # year
                    int(now.strftime("%m")), # month
                    int(now.strftime("%d")), # day
                    row.hour, # hour
                    row.minute, # minute
                    int(now.strftime("%w"))  # weekday
                    )

                # print(now)
                # print(due)
                # print(now - due)

                lookahead = timedelta(minutes=10)
                cutoff = due - lookahead

                if now >= cutoff: # send messsgae
                    reminders.append(dict(row._asdict()))
                    print(f"Reminder due: {row}")
 
                if now < cutoff: # wait
                    print(f"Reminder not due: {row}")

                # print(row.day)

            batch_time = time.perf_counter() - batch_start
            print(f"Batch completed in {batch_time}s")

    conn.close()
    return reminders

def complete_reminder(num_from):
    """ Marks a reminder as complete. """
    # get number's most recent reminder
    # mark that reminder as complete
    success = False
    if success:
        return 1
    else:
        return 0

def send_reminders(reminders):
    """ Sends reminders batch one at a time. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            for reminder in reminders:

                # Get phone number
                cur.execute("SELECT number FROM numbers WHERE num_id=( \
                    SELECT num_id FROM reminders WHERE reminder_id=%s)", 
                    (reminder["reminder_id"],))
                number = cur.fetchone()
                print(f"number:{number.number}")

                # Get reminder text                
                cur.execute("SELECT text FROM reminders WHERE reminder_id=%s",
                    (reminder["reminder_id"],))
                text = cur.fetchone()
                print(f"text:{text.text}")

                if reminder["reminded"]:
                    iterations = int(reminder["reminded"])
                else:
                    iterations = 0

                # Get iterations
                message = (
                    f'{text.text}\n'
                    '\n'
                    f'due {reminder["hour"]}:{reminder["minute"]:02}\n'
                    f'reminder #{iterations + 1}\n'
                    '\n'
                    'Reply "yes" to complete.'
                    # '"Snooze [hour int]" to snooze'
                )

                print(f"message:\n{message}")

                if iterations >= 2:
                    message += "\nReminder being cancelled due to nonresponse."

                    # TODO actually cancel or snooze

                # send_msg(number.number, message)