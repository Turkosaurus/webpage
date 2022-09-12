""" Handles application database logic. """
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

def create_tables():
    """ Setup database tables. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS reminders_recurring ( \
                reminder_id SERIAL, \
                num_id INTEGER, \
                name VARCHAR(1024), \
                interval_hours INTEGER \
            )")

            cur.execute("CREATE TABLE IF NOT EXISTS reminders_queue ( \
                reminder_id INTEGER, \
                due TIMESTAMP, \
                pokes INTEGER, \
                completed BOOL, \
                completed_on TIMESTAMP \
            )")

def main():
    """ Main function. """
    create_tables()

if __name__ == '__main__':
    main()

