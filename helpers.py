import os
import psycopg2
import psycopg2.extras
import requests
import csv
import datetime
from flask import request
from functools import wraps

# PostgreSQL database connection
db = os.getenv('DATABASE_URL')

# File Handling for /data
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """ Check if an extension is valid. """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Record failure of database logging
def log_error(time, location, error):
    """ Writes errors locally when db write fails. """
    with open('log.csv', 'a', encoding="utf8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([time, location, error])


def file_store(filename, description):
    """ TODO: Stores file into database. """
    uploaded = datetime.datetime.utcnow().isoformat()
    return 0


def file_retrieve(id):
    """ Retrieves file from database via id, structure metadata. """

    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            # Download file by id, structure metadata
            cur.execute("SELECT * FROM files WHERE id=%s LIMIT 1", [id])
            data = cur.fetchone()
            cur.close()
            # print(f"data:{data}")

    conn.close()

    filedata = data[5]
    description = data[4]
    filetype = data[3]
    uploaded = (data[1])
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    uploaded_short = data[1].strftime("%B%Y")

    filename = f"{data[2]}.{filetype}"
    # print(f"Delivering file: {filename}")

    package =  {
        "filedata": filedata,
        "description": description,
        "filetype": filetype,
        "filename": filename,
        "uploaded_short": uploaded_short,
        "uploaded": uploaded
        }

    return package

# Pageviews
def count_pageview(page):
    """
    Counts pageviews to given routes
    """
    # https://www.psycopg.org/docs/usage.html
    with psycopg2.connect(db) as conn:

        errors = 0
        # obtain IP
        try:
            # Obtain client IP (even when proxy is used)
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                ip_address = request.environ['REMOTE_ADDR']
            else:
                ip_address = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
        except Exception as error:
            ip_address = error

        time = datetime.datetime.utcnow().isoformat()

        # Log pageview into db, or log error into log.csv
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
                cur.execute("INSERT INTO pageviews (time, ip, page) VALUES (%s, %s, %s)", (time, ip_address, page))
                conn.commit()

        except Exception as error:
            errors += 1
            log_error(time, 'count_pageview', error)
        
    conn.close()

    return errors


def retrieve_pageviews():
    """
    Allows viewing pageviews
    """
    # https://www.psycopg.org/docs/usage.html
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            cur = conn.cursor()
            cur.execute("SELECT * FROM pageviews ORDER BY time DESC LIMIT 100")
            pageviews = cur.fetchall()
            conn.commit()
            cur.close()
    return pageviews


### METAR ###

def fetch_metar(airport):
    """ Fetches metar .csv from aviationweather.gov """
    print(f"Fetching METAR for {airport}")

    # https://www.aviationweather.gov/adds/dataserver_current/current/
    metars = requests.get('https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv')
    url_content = metars.content

    result = 'error: unable to find METAR'

    csv_file = open('static/metars.csv', 'wb')
    csv_file.write(url_content)
    csv_file.close()

    with open('static/metars.csv', 'r', encoding="utf8") as csvfile:

        csv_reader = csv.reader(csvfile)

        header_found = False
        for row in csv_reader:

            # Skip all of the metadata before the headers
            if len(row) == 1:
                next(csv_reader)

            else:
                # Capture header if first time encoutering it
                if header_found is False:
                    header_found = True
                    # headers = row

                # Iterate through rows until match is found
                else:
                    if row[1] == airport.upper():
                        result = row[0]

    return result


# Strings and Formatting
def style_metar():
    """
    Emojify METAR nomenclature
    """

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

