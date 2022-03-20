import os
import psycopg2
import csv
import datetime
from flask import request
from functools import wraps


# PostgreSQL database connection
conn = psycopg2.connect(os.getenv('DATABASE_URL'))


# Pageviews
def count_pageview(page):

    # Record failure of database logging
    def log_error(time, location, error):
        with open('log.csv', 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([time, location, error])

    errors = 0
    # obtain IP
    try:
        # Obtain client IP (even when proxy is used)
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    except Exception as e:
        ip = e

    time = datetime.datetime.utcnow().isoformat()

    # Log pageview into db, or log error into log.csv
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO pageviews (time, ip, page) VALUES (%s, %s, %s)", (time, ip, page))
        conn.commit()
        cur.close()

    except Exception as e:
        errors += 1
        log_error(time, 'count_pageview', e)

    return errors

def retrieve_pageviews():
    cur = conn.cursor()
    cur.execute("SELECT * FROM pageviews ORDER BY time DESC LIMIT 100")
    pageviews = cur.fetchall()
    conn.commit()
    cur.close()
    return pageviews



# File Handling for /data
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Strings and Formatting
def style_metar():

# Emojify a METAR

    template_condensed = """
    ✈ KFOO ⏳ +0:21\n
    ➡ 10-20\n
    👀 10 🌤 FL025 ⛅ FL200\n
    🅰 3003 (A3003) 🌡/💦 18/12C\n    
    """

    template_expanded = """
    ✈ Airpor (KFOO)\n
    ⏳ 21 minutes ago (312355Z)\n
    ➡ 10 gusting 20 (27010G20)\n
    👀 10 miles (10SM)\n
    ⛅ FL200 (BKN200)\n
    🌤 FL025 (SCT025)\n
    🅰 3003 (A3003)\n
    🌡/💦 18C/12C (18/12)\n
    """

    wxkey = {   
            "wind" : {
                "N" : "⬇",
                "NE" : "↙",
                "E" : "⬅",
                "SE" : "↖",
                "S" : "⬆",
                "SW" : "↗",
                "W" : "➡",
                "NW" : "↘"
            },
            "cloud" : {
                "CLR" : "☀",
                "FEW" : "🌤",
                "BKN" : "⛅",
                "OVC" : "☁"
            },
            "weather" : {
                "snow" : "🌨️",
                "rain" : "🌧️",
                "lightning" : "🌩️",
                "tornado" : "🌪️"
            },
            "temp" : "🌡️",
            "vis" : "👀",
            "altemiter" : "🅰️",
            "warning" : "⚠️"
        }

    return wxkey

