""" Completes cron tasks from Heroku Scheduler. """
import os
import time
import datetime
import psycopg2
import psycopg2.extras
import requests

from dotenv import load_dotenv
load_dotenv()

# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

print("Running cron_tasks.py...")

def main():
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            # Download file by id, structure metadata
            cur.execute("SELECT * FROM reminders_recurring")
            data = cur.fetchone()
            cur.close()
            print(f"Recurring reminders fetched!\n{data}")

    conn.close()

    # content = "foo"
    # r = requests.get('https://www.turkosaur.us/ping/%s' % content)
    # print(r)

if __name__ == '__main__':
    main()
