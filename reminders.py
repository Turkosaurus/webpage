""" Reminders functions """
import os
import time
import datetime
from datetime import timedelta
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

def get_reminders():
    """ Retrieves all reminders from database. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            now = datetime.datetime.now()
            cur.execute("SELECT * FROM reminders_schedule \
                WHERE day=%s AND active=True", (now.strftime("%w")))
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

    conn.close
    return reminders

def send_reminders(reminders):
    """ Sends reminders batch one at a time. """
    for reminder in reminders:
        print(f"Sending reminder {reminder}")
