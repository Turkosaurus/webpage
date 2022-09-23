import os
import psycopg2
import psycopg2.extras
import datetime
from dotenv import load_dotenv

""" Handles application database logic. """

from dotenv import load_dotenv
load_dotenv()

# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

def create_tables():
    """ Setup database tables for reminders. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS reminders ( \
                reminder_id SERIAL, \
                text VARCHAR(1024), \
                num_id INTEGER, \
                active BOOL \
            )")

            cur.execute("CREATE TABLE IF NOT EXISTS reminders_schedule ( \
                reminder_id INTEGER, \
                day INTEGER, \
                hour INTEGER, \
                minute INTEGER, \
                reminded INTEGER, \
                active BOOL, \
                completed_on TIMESTAMP, \
                recurring BOOL \
            )")

text = "apix 5mg"
schedule = [ # [day, hour, minute]
    [0, 10, 00],
    [0, 20, 00],
    [1, 10, 00],
    [1, 20, 00],
    [2, 10, 00],
    [2, 20, 00],
    [3, 10, 00],
    [3, 20, 00],
    [4, 10, 00],
    [4, 20, 00],
    [5, 10, 00],
    [5, 20, 00],
    [6, 10, 00],
    [6, 20, 00]
]

def add_reminders(text, schedule):
    """ Setup database tables. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("INSERT INTO reminders (text, num_id, active) \
                VALUES (%s, 5, true)", (text,))

            for reminder in schedule:
                # Twice daily for a week
                cur.execute(f"INSERT INTO reminders_schedule \
                    (reminder_id, day, hour, minute, active) \
                    VALUES (1, {reminder[0]}, {reminder[1]}, {reminder[2]}, True) \
                ")

def backup_tables():
    """ Setup database tables. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            tables = [
                "nail_boxes",
                "nail_boxprod",
                "nail_boxused",
                "nail_colors",
                "nail_cycles",
                "nail_items",
                "nail_loterias",
                "nail_parts",
                "nail_projections",
                "nail_queueitems",
                "nail_queueparts",
                "nail_shirts",
                "nail_sizes",
                "nail_types",
                "nail_users"
            ]
            for table in tables:
                # backup table
                cur.execute(f"DROP TABLE IF EXISTS {table}_backup")
                cur.execute(f"CREATE TABLE IF NOT EXISTS {table}_backup as \
                    (SELECT * from {table}) \
                ")
    # conn.close()

def drop_tables():
    """ Setup database tables. """
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("DROP TABLE IF EXISTS reminders")
            cur.execute("DROP TABLE IF EXISTS reminders_schedule")
    conn.close()

def main():
    """ Main function. """
    drop_tables()
    create_tables()
    add_reminders(text, schedule)
    # backup_tables()

if __name__ == '__main__':
    main()

