""" Flask main application. """

import os
import csv
import re
import datetime
import logging
from flask import Flask, \
    render_template, send_file, url_for, redirect, flash, request, send_from_directory, \
    abort, session, current_app, make_response
from flask_session import Session

from functools import wraps

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import requests
from reminders import complete_reminder

from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from io import BytesIO

# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import psycopg2
import psycopg2.extras


from helpers import \
    allowed_file, style_metar, count_pageview, retrieve_pageviews, \
    file_store, file_retrieve, fetch_metar

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
db = os.getenv('DATABASE_URL')


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

### DECORATORS ###

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

def validate_twilio_request(f):
# https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests#
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

def send_text(recipient, message):
    """ Sends Twilio message. """
    message = client.messages.create(
        body=message,
        messaging_service_sid=messaging_service_sid,
        to=recipient
    )


# ### SELENIUM ###

# def  load_driver():
#     """ Loads Selenium driver. """
#     # https://elements.heroku.com/buildpacks/pyronlaboratory/heroku-integrated-firefox-geckodriver

#     options = webdriver.FirefoxOptions()
	
# 	# enable trace level for debugging 
# 	options.log.level = "trace"

# 	options.add_argument("-remote-debugging-port=9224")
# 	options.add_argument("-headless")
# 	options.add_argument("-disable-gpu")
# 	options.add_argument("-no-sandbox")

# 	binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))

# 	firefox_driver = webdriver.Firefox(
# 		firefox_binary=binary,
# 		executable_path=os.environ.get('GECKODRIVER_PATH'),
# 		options=options)

# 	return firefox_driver

# def scrape():
#     """ Web scraping functions for Selenium. """
#     # Selenium options
#     # opts = Options()
#     # opts.set_headless()
#     # assert opts.headless  # Operating in headless mode
#     # browser = Firefox(options=opts)

#     browser = load_driver()
#     browser.get('https://www.turkosaur.us')

#     # Search and return results
#     element = browser.find_element_by_id('name')
#     element.send_keys('testname')

#     element = browser.find_element_by_id('email')
#     element.send_keys('test@email.com')

#     element = browser.find_element_by_id('message')
#     element.send_keys('Looks like we made it. 🐱‍🐉')

#     element.submit()

#     browser.close()

#     # results = browser.find_elements_by_class_name('result_body')
#     # print(results[0].text)
#     # print(results[0].text)
#     return 0


### HELPERS ###


def send_msg(recipient, message):
    """ Sends Twilio text message. """
    message = client.messages.create(
        body = message,
        # status_callback='https://www.turkosaur.us/message/status',
        messaging_service_sid=messaging_service_sid,
        to = recipient
    )

    return 0

@app.route("/backup/<table>")
@login_required
def backup(table):
    print("BACKUP")

    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY id ASC;")
        data = cur.fetchall()
        cur.close()

        with open(f'{table}.csv', 'a', encoding="utf8") as file:
            writer = csv.writer(file)

            for line in data:
                writer.writerow(line)
        flash("Backup complete.")
        return redirect("/admin")

    except Exception as e:
        flash(e)
        return redirect("/admin")


### ROUTES ###

# @app.route("/test")
# @login_required
# def test():
#     return redirect('/')

@app.route("/")
def home():
    count_pageview('/')
    return render_template("index.html")

@app.route("/status")
def status():
    return render_template("index.html")

@app.route("/admin")
@login_required
def admin():

    count_pageview('/admin')
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            #TODO this is probably wrong, results is none, but records populates
            cur.execute("SELECT * FROM logs")
            logs = cur.fetchall()
            pageviews = retrieve_pageviews()
        
    conn.close()

    return render_template("admin.html", logs=logs, pageviews=pageviews)

# @app.route("/admin/<action>", methods=['POST'])
# @login_required
# def admin_edit(action):

#     if action == 'resume':
#         version = request.form.get('version')

@app.route("/keg")
def keg():
    """
    Keg Weight Worksheet
    """
    count_pageview('/keg')
    scripts = "static/keg.js"
    return render_template("keg.html", scripts=scripts)


@app.route("/ping/<content>", methods=['GET'])
def ping(content):

    recipient = number_turk

    message = f"turkosaurus message\ncontent:\n{content}"

    send_text(recipient, message)
 
    flash("Thank you. We'll be in touch soon!")

    return redirect('/')


@app.route("/message", methods=['POST'])
@validate_twilio_request
def message_received():
    """
    Processes incoming Twilio messages
    """

    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            
            # Testing environment:
            if os.getenv('FLASK_DEBUG') == '1':
                body = """
                lorem ipsum
                foo foo froofy foo
                """

            else:
                # Send a dynamic reply to an incoming text message
                # Get the message the user sent our Twilio number
                body = request.values.get('Body', None)
                num_from = request.values.get('From', None)
                MessageSid = request.values.get('MessageSid', None)
                NumMedia = request.values.get('NumMedia', None) # The number of media items associated with your message

                # TODO consolidate into logging function
                cur.execute("SELECT * FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
                existing = cur.fetchone()
                if not existing:
                    time_now = datetime.datetime.utcnow().isoformat()
                    cur.execute("INSERT INTO numbers (number, notify, created_on) \
                        VALUES (%s, %s, %s)",
                        (num_from, 'False', time_now))

                cur.execute("SELECT num_id \
                    FROM numbers \
                    WHERE number=%(num_from)s",
                    {'num_from': num_from})
                num_id = cur.fetchone()[0]
                print(f"Creating activity for num_id:{num_id}")

                time_now = datetime.datetime.utcnow().isoformat()
                activity = "message"
                cur.execute("INSERT INTO activity (num_id, timestamp, activity, messagesid) \
                    VALUES (%s, %s, %s, %s)",
                    (num_id, time_now, activity, MessageSid))

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

            if body == "yes" or "Yes" or "YES":
                success = complete_reminder(num_from)
                if success:
                    response_match = True

            # if 'Punch time' in body:
            #     response_match = True
            #     # timedata = punch()
            #     resp.message(f"Time Card\n---\n{timedata}")

            if response_match is False:

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
    conn.close()
    return str(resp)


@app.route("/message/status", methods=['GET', 'POST'])
def message_status():
    """ Callback for Twilio message statuses. """
    # https://www.twilio.com/docs/sms/tutorials/how-to-confirm-delivery-python

    message_sid = request.values.get('MessageSid', None)
    message_status = request.values.get('MessageStatus', None)
    num_from = request.values.get('From', None)

    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            # Find existing number id, or create new one if not existing
            cur = conn.cursor()
            cur.execute("SELECT * FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
            existing = cur.fetchone()
            if not existing:
                time = datetime.datetime.utcnow().isoformat()
                cur.execute("INSERT INTO numbers (number, notify, created_on) VALUES (%s, %s, %s)", (num_from, 'False', time))

            # TODO move this up and consolidate, as it's a redundant query
            cur.execute("SELECT num_id FROM numbers WHERE number=%(num_from)s", {'num_from': num_from})
            num_id = cur.fetchone()[0]
            print(f"Creating activity for num_id:{num_id}")

            time = datetime.datetime.utcnow().isoformat()
            activity = "callback"
            cur.execute("INSERT INTO activity (num_id, timestamp, activity, messagesid, status) VALUES (%s, %s, %s, %s, %s)", (num_id, time, activity, message_sid, message_status))

            conn.commit()
            cur.close()
    
    conn.close()
    return ('', 204)


@app.route("/metar", methods=['GET', 'POST'])
def metar():
    """
    Servers
    """
    # https://www.psycopg.org/docs/usage.html
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            count_pageview('/metar')

            if request.method == 'GET':
                return render_template('cluck.html')

            # POST
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

                    msg_signup = "Thanks for signing up! Reply 'METAR KAUS' or 'METAR KLAX' for weather."
                    send_msg(number, msg_signup)

                    flash("Thank you. We'll be in touch soon!")

        return redirect("/metar")


@app.route("/metar/now", methods=['POST'])
def metar_button():
    """ Delivers METAR to browser via Flash message. """

    airport = request.form.get("airport")

    metar_result = fetch_metar(airport)
    flash(f"{metar_result}")
    return redirect("/metar")


@app.route("/data", methods=['GET', 'POST'])
def data():
    """ Processes submitted csv and returns changes. """
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

            # Read into a SQL table
            with open(f'static/uploads/{filename_user}', 'r', encoding="utf8") as csvfile:

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



            with open(f'static/uploads/{filename_user}', 'w', encoding="utf8") as csvfile:

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
    """ Delivers resume. """

    count_pageview(f'/resume')

    # TODO add authorizations/click tracking
    # https://www.psycopg.org/docs/usage.html
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

            # Find most recent public resume
            cur = conn.cursor()
            cur.execute("SELECT id FROM files WHERE description=%s ORDER by uploaded DESC LIMIT 1;", ["resume_public"])
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


@app.route("/<shorturl>")
def short_url(shorturl):
    """ Catches all other URL requests, can be used for temp URLs. """
    count_pageview(shorturl)

    #URL shortener

    print(f"short_url:{shorturl}")
    return redirect("/")


# @app.route("/secret/<key>")
# def secret(key):
#     count_pageview(f"secret/{key}")
#     # Lookup links table to enable logic here

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


@app.route("/upload", methods=['POST'])
@login_required
def pdf_upload():
    """ Uploads a file to the database. """

    count_pageview('/upload')

    version = request.form.get('version')

    if version == 'public':
        filename = 'resume_TravisTurk_web'
        description = 'resume_public'

    if version == 'private':
        filename = 'resume_TravisTurk'
        description = 'resume_private'

    # https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/

    # check if the post request has the file part
    if 'inputfile' not in request.files:
        flash('No file part')
        return redirect("/admin")

    file = request.files['inputfile']
    # filename_override = request.form.get('filename_override')

    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect("/admin")

    print(file)
    print(filename)
    print(file.filename)
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    print(allowed_file(file.filename))

    # TODO reinstitute checks for public files
    if file and allowed_file(file.filename):
        # filename = secure_filename(file.filename) # original filenames kept
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    # else:
    #     flash('Upload Error')
    #     return redirect("/admin")
        # # Read into a SQL table
        # with open(f'static/uploads/{filename_user}', 'r') as csvfile:


    # Default file metadata
    uploaded = datetime.datetime.utcnow().isoformat()
    filetype = "pdf" # TODO infer filetypes to make this more generic

    # Open file, convert to bytes
    file = open(f"{app.config['UPLOAD_FOLDER']}/{filename}.{filetype}", 'rb')
    filedata = file.read()
    file.close()
    filedata = bytes(filedata)
    # print(f"filedata:{filedata}")

    # Insert into database
    # https://www.psycopg.org/docs/usage.html
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("INSERT INTO files (uploaded, name, filetype, description, filedata) \
                VALUES (%s, %s, %s, %s, %s)",
                (uploaded, filename, filetype, description, filedata))
            conn.commit()
            cur.close()
    conn.close()
    flash(f"{filename}.{filetype} ({description})saved to database.")
    return redirect('/admin.html')


###### USER ACCOUNTS ####
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    count_pageview('/register')

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

        # https://www.psycopg.org/docs/usage.html
        with psycopg2.connect(db) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

                # Check if username is already taken
                cur.execute("SELECT username FROM users WHERE username LIKE %s;", [username])
                matches = cur.fetchall()

                if not matches:

                    # Add the username
                    time_now = datetime.datetime.utcnow().isoformat()
                    cur.execute("INSERT INTO users (username, password, created_on) VALUES (%s, %s, %s)",
                                [username, hashedpass, time_now])
                    conn.commit()

                else:
                    flash("Username invalid or already taken.")

        conn.close()
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
            flash("Username required")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Password Required")
            return render_template("login.html")

        username = request.form.get("username")

        # https://www.psycopg.org/docs/usage.html
        with psycopg2.connect(db) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

                # Query database for username
                cur.execute("SELECT * FROM users WHERE username=%s;", [username])
                rows = cur.fetchall()

                # Ensure username exists
                if len(rows) != 1:
                    print("loginerror")
                    flash("Login Error")
                    # conn.close()
                    return render_template("login.html")

                # Ensure username exists and password is correct
                if not check_password_hash(rows[0][2], request.form.get("password")):

                    # # TODO implement fancier backoff
                    # time.sleep(5)
                    print("passworderror")

                    flash("Password Error")
                    # conn.close()
                    return render_template("login.html")

                # Remember which user has logged in
                session["user_id"] = rows[0][0]

                # Update "last_login"
                lastlogin = datetime.datetime.utcnow().isoformat()
                cur.execute("UPDATE users SET last_login=%s WHERE id=%s", [lastlogin, session["user_id"]])
                conn.commit()

        # conn.close()

        # Redirect user to home page
        flash(f"Welcome, {username}")
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    count_pageview('/logout')

   # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Session Cleared")
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
