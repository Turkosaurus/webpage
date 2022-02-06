from flask import Flask, render_template, send_file, url_for, redirect, flash, request, send_from_directory, abort, session, current_app, make_response
from flask_session import Session

from functools import wraps

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
import requests
from twilio.rest import Client
import os
import csv
import re
import time # TODO replace all use of time with datetime
import datetime
import logging


from io import BytesIO

# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import psycopg2

from werkzeug.utils import secure_filename
from data import allowed_file

# import threading
# import discord
from dotenv import load_dotenv

load_dotenv()

# Import Authorized User List
authusers = []
authusers.append(os.getenv('USERA'))

logging.basicConfig(level=logging.INFO)


# Flask App
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


# PostgreSQL database connection
conn = psycopg2.connect(os.getenv('DATABASE_URL'))

# Twilio configuration
messaging_service_sid = os.getenv('TWILIO_MESSAGING_SERVICE_SID')
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
number_turk = os.getenv('NUMBER_TURK')
number_cluck = os.getenv('NUMBER_CLUCK')
client = Client(account_sid, auth_token)

# App - Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SESSION_PERMANENT"] = False
# app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=0.001)
app.config["SESSION_TYPE"] = "filesystem"
# app.config["SESSION_TYPE"] = "null"

app.config['UPLOAD_FOLDER'] = os.getenv('PWD') + "/static/uploads"


Session(app)

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests#
def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''))

        # Continue processing the request if it's valid, return a 403 error if
        # it's not
        if request_valid:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


def  load_driver():
    # https://elements.heroku.com/buildpacks/pyronlaboratory/heroku-integrated-firefox-geckodriver

	options = webdriver.FirefoxOptions()
	
	# enable trace level for debugging 
	options.log.level = "trace"

	options.add_argument("-remote-debugging-port=9224")
	options.add_argument("-headless")
	options.add_argument("-disable-gpu")
	options.add_argument("-no-sandbox")

	binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))

	firefox_driver = webdriver.Firefox(
		firefox_binary=binary,
		executable_path=os.environ.get('GECKODRIVER_PATH'),
		options=options)

	return firefox_driver


def punch():

    # Selenium options
    # opts = Options()
    # opts.set_headless()
    # assert opts.headless  # Operating in headless mode
    # browser = Firefox(options=opts)
    browser = load_driver()
    browser.get('https://workforcenow.adp.com/theme/index.html#/Myself_ttd_MyselfTabTimecardsAttendanceSchCategoryMyTimeEntry/MyselfTabTimecardsAttendanceSchCategoryMyTimeEntry')

    # Login to ADP
    form_username = browser.find_element_by_id('login-form_username')
    username = os.getenv('APS_USERNAME')
    form_username.send_keys(username)
    form_username.send_keys(Keys.RETURN)
    print(f"Username {username} entered.")

    time.sleep(5)

    form_password = browser.find_element_by_id('login-form_password')
    password = os.getenv('APS_PASSWORD')
    form_password.send_keys(password)
    print(f"Password entered.")

    form_submit = browser.find_element_by_id('signBtn')
    form_submit.submit()

    print("Waiting for page to load...")
    time.sleep(5)
    form_submit.send_keys(Keys.ESCAPE)

    punches = browser.find_element_by_id('form1')
    print(punches)

    print(driver.page_source)


    # https://realpython.com/modern-web-automation-with-python-and-selenium/
    # results = browser.find_elements_by_class_name('result')
    # print(results[0].text)
    
    browser.close()

    return punches


def scrape():
    # Selenium options
    # opts = Options()
    # opts.set_headless()
    # assert opts.headless  # Operating in headless mode
    # browser = Firefox(options=opts)

    browser = load_driver()
    browser.get('https://www.turkosaur.us')

    # Search and return results
    element = browser.find_element_by_id('name')
    element.send_keys('testname')

    element = browser.find_element_by_id('email')
    element.send_keys('test@email.com')

    element = browser.find_element_by_id('message')
    element.send_keys('Looks like we made it. 🐱‍🐉')

    element.submit()

    browser.close()


    # results = browser.find_elements_by_class_name('result_body')
    # print(results[0].text)
    # print(results[0].text)


def fetch_metar(airport):
    print(f"Fetching METAR for {airport}")

    # https://www.aviationweather.gov/adds/dataserver_current/current/
    metars = requests.get('https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv')
    url_content = metars.content

    result = 'error: unable to find METAR'

    csv_file = open('static/metars.csv', 'wb')
    csv_file.write(url_content)
    csv_file.close()

    with open('static/metars.csv', 'r') as csvfile:

        csv_reader = csv.reader(csvfile)

        header_found = False
        for row in csv_reader:

            # Skip all of the metadata before the headers
            if len(row) == 1:
                next(csv_reader)

            else:
                # Capture header if first time encoutering it
                if header_found == False:
                    header_found = True
                    # headers = row

                # Iterate through rows until match is found
                else:
                    if row[1] == airport.upper():
                        result = row[0]

    return (result)


def send_msg(recipient, message):
    message = client.messages.create(
        body = message,
        # status_callback='https://www.turkosaur.us/message/status',
        messaging_service_sid=messaging_service_sid,
        to = recipient
    )

    return 0


def count_pageview(page):

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

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO pageviews (time, ip, page) VALUES (%s, %s, %s)", (time, ip, page))
        conn.commit()
        cur.close()

    except Exception as e:
        errors += 1
        log_error(time, 'count_pageview', e)

    return errors


def log_error(time, location, error):
    with open('log.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([time, location, error])


def retrieve_pageview():
    cur = conn.cursor()
    cur.execute("SELECT * FROM pageviews")
    pageviews = cur.fetchall()
    conn.commit()
    cur.close()
    return pageviews


def style_metar():

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


def file_store(filename, description):
    uploaded = datetime.datetime.utcnow().isoformat()
    return 0

def file_retrieve(id):

    # Download file by id, structure metadata
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE id=%s", [id])
    data = cur.fetchone()
    cur.close()
    # print(f"data:{data}")

    filedata = data[5]
    description = data[4]
    filetype = data[3]
    uploaded = datetime.datetime.fromisoformat(str(data[1]))
    uploaded_short = data[1].strftime("%B%Y")

    filename = f"{data[2]}.{filetype}"
    # print(f"Delivering file: {filename}")

    return {"filedata": filedata, "description": description, "filetype": filetype, "filename": filename, "uploaded_short": uploaded_short, "uploaded": uploaded}


# ROUTES #

# @app.route("/test")
# def test():
#     count_pageview('/test')

#     result = punch()
#     print(result)
#     scrape()

#     return redirect('/')


@app.route("/")
def home():
    count_pageview('/')
    return render_template("index.html")


@app.route("/admin")
def admin():

    data = retrieve_pageview()
    return render_template("admin.html", data=data)

@app.route("/portfolio")
def portfolio():
    count_pageview('/portfolio')

    return render_template("projects.html")


@app.route("/ping", methods=['POST'])
def ping():

    recipient = number_turk
    name = request.form.get("name")
    contact = request.form.get("email")
    message = request.form.get("message")
    print(f"{name} {contact} {message}")

    message = f"turkosaurus message\nfrom: {name}\n{contact}\n---\n{message}"

    message = client.messages \
        .create(
            body=message,
            messaging_service_sid=messaging_service_sid,
            to=recipient
        )

    flash("Thank you. We'll be in touch soon!")

    return redirect('/')


@app.route("/message", methods=['POST'])
@validate_twilio_request
def message():

    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    num_from = request.values.get('From', None)
    MessageSid = request.values.get('MessageSid', None)
    NumMedia = request.values.get('NumMedia', None) # The number of media items associated with your message

    # TODO consolidate into logging function
    cur = conn.cursor()
    cur.execute("SELECT * FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
    existing = cur.fetchone()
    if not existing:
        time = datetime.datetime.utcnow().isoformat()
        cur.execute("INSERT INTO numbers (number, notify, created_on) VALUES (%s, %s, %s)", (num_from, 'False', time))

    cur.execute("SELECT num_id FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
    num_id = cur.fetchone()[0]
    print(f"Creating activity for num_id:{num_id}")

    time = datetime.datetime.utcnow().isoformat()
    activity = "message"
    cur.execute("INSERT INTO activity (num_id, timestamp, activity, messagesid) VALUES (%s, %s, %s, %s)", (num_id, time, activity, MessageSid))

    conn.commit()
    cur.close()


    print("Message received:")
    print(f"from: {num_from}\n")
    print(f"body: {body}")

    # Start our TwiML response
    resp = MessagingResponse()

    response_match = False
    
    metar_words = ['METAR', 'Metar', 'metar']
    if any(x in body for x in metar_words):
        response_match = True

        # Find all airports in text
        airports = re.findall("([Kk]...)", body)
        # airports = airports.strip()

        print(f"Found airports: {airports}")

        # TODO iterate to loop through each airport that matches
        metar = fetch_metar(airports[0])
        resp.message(f"METAR {airports[0]}\n{metar}")        

    if 'Punch time' in body:
        response_match = True
        timedata = punch()
        resp.message(f"Time Card\n---\n{timedata}")

    if response_match == False:

        resp.message(f"MENU\n✈ Reply 'METAR K---' for aviation weather\n")

        # Check for Main Menu
        # menu_words = ['INFO', 'Info' 'info', 'MENU', 'Menu', 'menu', 'OPTIONS', 'Options', 'options']
        # if any(x in body for x in menu_words):
            # response_match = True
            # resp.message(f'''
            # __MENU__
            # METAR K___
            # ''')
            # "Punch time/in/out"\n

    return str(resp)


@app.route("/message/status", methods=['GET', 'POST'])
def message_status():

    # BUG not currently proven functional
    # TODO consolidate into logging function
    # https://www.twilio.com/docs/sms/tutorials/how-to-confirm-delivery-python
    message_sid = request.values.get('MessageSid', None)
    message_status = request.values.get('MessageStatus', None)
    num_from = request.values.get('From', None)

    cur = conn.cursor()
    cur.execute("SELECT * FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
    existing = cur.fetchone()
    if not existing:
        time = datetime.datetime.utcnow().isoformat()
        cur.execute("INSERT INTO numbers (number, notify, created_on) VALUES (%s, %s, %s)", (num_from, 'False', time))

    cur.execute("SELECT num_id FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
    num_id = cur.fetchone()[0]
    print(f"Creating activity for num_id:{num_id}")

    time = datetime.datetime.utcnow().isoformat()
    activity = "callback"
    cur.execute("INSERT INTO activity (num_id, timestamp, activity, messagesid, status) VALUES (%s, %s, %s, %s, %s)", (num_id, time, activity, message_sid, message_status))

    conn.commit()
    cur.close()

    return ('', 204)


@app.route("/metar", methods=['GET', 'POST'])
def metar():
    count_pageview('/metar')
    
    if request.method == 'GET':
        return render_template('cluck.html')

    # Post
    else:
        number = request.form.get("number")
        notify = request.form.get("notify")
        if notify != 'true':
            notify = False

        print(f"number:{number}")

        # Convert to E.164 per 
        # https://www.twilio.com/docs/lookup/tutorials/validation-and-formatting#validate-a-national-phone-number
        try:
            phone_number = client.lookups \
                        .v1 \
                        .phone_numbers(number) \
                        .fetch(country_code='US')

        except:
            flash("Invalid Number")

        else:
            number = phone_number.phone_number
            print(f"received text from:{number}")

            cur = conn.cursor()
            # cur.execute("SELECT * FROM numbers")
            cur.execute("SELECT * FROM numbers WHERE number=%(number)s", {'number': number})

            existing = cur.fetchall()

            print(f"existing:{existing}")

            if not existing:
                time = datetime.datetime.utcnow().isoformat()
                cur.execute("INSERT INTO numbers (number, notify, created_on) VALUES (%s, %s, %s)", (number, notify, time))

            elif notify == 'true':
                cur.execute("UPDATE numbers SET notify = 'true' WHERE number=%(number)s", {'number': number})

            elif notify == 'false':
                cur.execute("UPDATE numbers SET notify = 'true' WHERE number=%(number)s", {'number': number})

            conn.commit()
            cur.close()

            message = "Thanks for signing up for METAR by SMS by Turkosaurus. Reply 'METAR KAUS' or 'METAR KLAX' for weather."
            send_msg(number, message)

            flash("Thank you. We'll be in touch soon!")

        return redirect("/metar")


@app.route("/metar/now", methods=['POST'])
def metar_button():

    airport = request.form.get("airport")

    metar = fetch_metar(airport)
    flash(f"{metar}")
    return redirect("/metar")


@app.route("/data", methods=['GET', 'POST'])
def data():
    count_pageview('/data')

    data = []

    if request.method == 'GET':
        return render_template("data.html", data=data)


    else:
        delivery = request.form.get('delivery')

        # https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/

        # check if the post request has the file part
        if 'inputfile' not in request.files:
            flash('No file part')
            return redirect("/data")

        file = request.files['inputfile']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect("/data")

        if file and allowed_file(file.filename):
            filename_user = secure_filename(file.filename) # User supplied filenames kept
            # filename = 'tmp.csv'
            print(f"filename:{filename_user}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_user))

            # Read loterias.csv into a SQL table
            with open(f'static/uploads/{filename_user}', 'r') as csvfile:

                print(f'Reading {filename_user}...')
                csv_reader = csv.reader(csvfile)

                # next(csv_reader)
                row_counter = 0

                negatives = []

                for row in csv_reader:
                    data.append(row)

                for row in data:
                    print(row)
                    for i in range(len(row)):
                        try:
                            if int(row[i]) < 0:
                                print(f"found a negative value ({row[i]}) on row {row_counter}")
                                row[i] = abs(int(row[i]))
                                negatives.append(row_counter + 1)

                        except:
                            print("EXCEPTION")

                    row_counter += 1


            # TODO save as binary object
            # https://www.postgresqltutorial.com/postgresql-python/blob/



            with open(f'static/uploads/{filename_user}', 'w') as csvfile:

                scribe = csv.writer(csvfile)

                for row in data:
                    scribe.writerow(row)

            flash(f"File uploaded. {row_counter} rows assessed.")
            if negatives:
                flash(f"Negative values found and converted on row {negatives}")

            if delivery == 'download':
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename_user, attachment_filename=filename_user, as_attachment=True, mimetype='text/csv')

            if delivery == 'view':
                return render_template("data.html", data=data)

        return redirect('/data')


@app.route("/resume")
def resume():

    count_pageview(f'/resume')

    # TODO add authorizations/click tracking

    # Find most recent public resume
    cur = conn.cursor()
    cur.execute("SELECT id FROM files WHERE description=%s ORDER by ID DESC LIMIT 1;", ["resume_public"])
    id = cur.fetchone()[0]
    print(f"Most recent resume_public: id = {id}")
    cur.close()

    file = file_retrieve(id)

    # # LOCAL - Create new local file
    # with open("static/uploads/resume-recent.pdf", "wb") as f:
    #     print((file['filedata']))
    #     f.write(file['filedata'])

    # EMBED
    # https://stackoverflow.com/questions/18281433/flask-handling-a-pdf-as-its-own-page
    # https://flask.palletsprojects.com/en/2.0.x/api/#flask.make_response

    response = make_response(bytes(file['filedata']))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s' % file['filename']

    return response

# TODO move this into admin
@app.route("/logs")
def logs():
    count_pageview('/logs')

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    #TODO this is probably wrong, results is none, but records populates
    cur.execute("SELECT * FROM logs")

    # Retrieve query results
    records = cur.fetchall()

    pageviews = retrieve_pageview()

    print(f"records:{records}")
    print(f"pageviews:{pageviews}")

    return redirect("/")


@app.route("/<shorturl>")
def short_url(shorturl):
    count_pageview(shorturl)

    #URL shortener

    print(f"short_url:{shorturl}")
    return redirect("/")


@app.route("/secret/<key>")
def secret(key):
    count_pageview(f"secret/{key}")
    # Lookup links table to enable logic here

# @app.route("/pdf")
# def pdf():
#     count_pageview('/pdf')

#     return send_file('static/resume-TravisTurk-web.pdf', mimetype='pdf', as_attachment=True, attachment_filename='resume.TravisTurk.pdf')

# @app.route("/file/<id>")
# @login_required
# def file(id):

#     # Retrieve file from database, generate file object from data using BytesIO()
#     file = file_retrieve(id)
#     data = BytesIO(file['filedata'])
  
#     return send_file(data, mimetype=file['filetype'], as_attachment=True, attachment_filename=file['filename'])


# @app.route("/pdf-upload")
# def pdf_upload():
#     count_pageview('/pdf-upload')

#     # Default file metadata
#     uploaded = datetime.datetime.utcnow().isoformat()
#     name = "resume_TravisTurk"
#     filetype = "pdf"
#     description = "resume_public"

#     # Open file, convert to bytes
#     file = open('static/resume-TravisTurk-web.pdf', 'rb')
#     filedata = file.read()
#     file.close()
#     filedata = bytes(filedata)
#     # print(f"filedata:{filedata}")
        
#     # Insert into database
#     cur = conn.cursor()
#     cur.execute("INSERT INTO files (uploaded, name, filetype, description, filedata) VALUES (%s, %s, %s, %s, %s)", (uploaded, name, filetype, description, filedata))
#     conn.commit()
#     cur.close()
#     print("File saved to database.")

#     # Find newest file
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM files;")
#     ids = cur.fetchall()
#     id = max(ids)[0]
#     print(f"max_id:{id}")
#     cur.close()

#     # Retrieve file from database
#     file = file_retrieve(id)
#     data = BytesIO(file['filedata'])
  
#     return send_file(data, mimetype=filetype, as_attachment=True, attachment_filename=file['filename'])

 


###### USER ACCOUNTS ####
#TODO write HMTL files, add @login required pdf submission for updated resume

@app.route("/register", methods=["GET", "POST"])
def register():
    count_pageview('/register')

    """Register user"""

    # Serve registration page
    if request.method == 'GET':
        return render_template("register.html")

    # Process submitted form responses on POST
    else:

        # Error Checking
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Username required.")
            return redirect('/register')

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Password required.")
            return redirect('/register')

        # Ensure password and password confirmation match
        if request.form.get("password") != request.form.get("passwordconfirm"):
            flash("Passwords must match.")
            return redirect('/register')

        # Ensure minimum password length
        if len(request.form.get("password")) < 8:
            flash("Password must be at least 8 characters.")
            return redirect('/register')

        # Store the hashed username and password
        username = request.form.get("username")
        hashedpass = generate_password_hash(request.form.get("password"))

        if username not in authusers:
            flash("Unauthorized user.")
            return redirect('/')

        #TODO #TURK-112 incoporate this new psychopg paradigm into this, replacing all db objects
        # Check if username is already taken
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username LIKE %s;", [username])
        matches = cur.fetchall()

        if not matches:

            # Add the username
            time = datetime.datetime.utcnow().isoformat()
            cur.execute("INSERT INTO users (username, password, created_on) VALUES (%s, %s, %s)",
                        [username, hashedpass, time])
            conn.commit()
            cur.close()
            return redirect("/")

        else:
            cur.close()
            flash("Username invalid or already taken.")
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    count_pageview('/login')

    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", errcode=400, errmsg="Username required.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", errcode=400, errmsg="Password required.")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists
        if len(rows) != 1:
            return render_template("register.html", errmsg="Username not found.")

        # Ensure username exists and password is correct
        if not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("error.html", errcode=403, errmsg="Incorrect password.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Update "last_login"
        time = datetime.datetime.utcnow().isoformat()
        db.execute("UPDATE users SET last_login=:time WHERE id=:id", time=time, id=session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    count_pageview('/logout')
    """Log user out"""

   # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



# if __name__ == '__main__':
#     app.run()



# tWebpage = threading.Thread(target=webpage)
# tWebpage.start()

# tWebpage = threading.Thread(target=webpage)
# tWebpage.start()

# load_dotenv()

# def cluck():
#     print("Waking Cluck...")

#     TOKEN = os.getenv('DISCORD_TOKEN')

#     client = discord.Client()

#     @client.event
#     async def on_ready():
#         print(f'{client.user} has connected to Discord!')

#     client.run(TOKEN)
#     flash("Cluck is in the coop.")

# tCluck = threading.Thread(target=cluck)
# tCluck.start()
