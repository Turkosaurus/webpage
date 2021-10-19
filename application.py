from flask import Flask, render_template, send_file, url_for, redirect, flash, request
from flask_session import Session
from twilio.twiml.messaging_response import MessagingResponse
import requests
from twilio.rest import Client
import os
import csv
import re
import time # TODO replace all use of time with datetime
import datetime
# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import psycopg2

# import threading
# import discord
from dotenv import load_dotenv

load_dotenv()

# Flask App
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


# PostgreSQL database connection
conn = psycopg2.connect(os.getenv('DATABASE_URL'))

# Twilio configuration
messaging_service_sid='MGd24392f1df2b12a99eb4b85d2bdd4aec'
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
number_turk = os.getenv('NUMBER_TURK')
client = Client(account_sid, auth_token)

# App - Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


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


    # https://realpython.com/modern-web-automation-with-python-and-selenium/
    # results = browser.find_elements_by_class_name('result')
    # print(results[0].text)
    
    browser.close()

    return punches


def scrape():
    # Selenium options
    opts = Options()
    opts.set_headless()
    assert opts.headless  # Operating in headless mode
    browser = Firefox(options=opts)
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

# ROUTES #

@app.route("/test")
def test():

    # result = punch()

    return redirect('/')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    return render_template("projects.html")


@app.route("/bio")
def bio():
    return render_template("bio.html")


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
def message():

    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    num_from = request.values.get('From', None)
    NumMedia = request.values.get('NumMedia', None) # The number of media items associated with your message

    print(f"Message received:")
    print(f"from: {num_from}\n")
    print(body)

    print("looping through the body")
    for item in body:
        print(item)

    # Start our TwiML response
    resp = MessagingResponse()

    # Check for Main Menu
    menu_words = ['INFO', 'Info' 'info', 'MENU', 'Menu', 'menu', 'OPTIONS', 'Options', 'options']
    if any(x in body for x in menu_words):
        resp.message(f'''
        MENU\n
        "METAR K___"\n
        ''')
        # "Punch time/in/out"\n
    
    metar_words = ['METAR', 'Metar', 'metar']
    if any(x in body for x in metar_words):

        # Find all airports in text
        airports = re.findall("([Kk]...)", body)
        # airports = airports.strip()

        print(f"Found airports: {airports}")

        # TODO iterate to loop through each airport that matches
        metar = fetch_metar(airports[0])
        resp.message(f"METAR {airports[0]}\n{metar}")        

    if 'Punch time' in body:
        timedata = punch()
        resp.message(f"Time Card\n---\n{timedata}")        

    return str(resp)


@app.route("/message/status")
def message_status():

    # https://www.twilio.com/docs/sms/tutorials/how-to-confirm-delivery-python
    return redirect('/')

@app.route("/metar", methods=['GET', 'POST'])
def metar():
    if request.method == 'GET':
        return render_template('cluck.html')

    # Post
    else:
        number = request.form.get("number")
        notify = request.form.get("notify")
        if notify != 'true':
            notify = False

        # Convert to E.164 per 
        # https://www.twilio.com/docs/lookup/tutorials/validation-and-formatting#validate-a-national-phone-number
        phone_number = client.lookups \
                     .v1 \
                     .phone_numbers(number) \
                     .fetch(country_code='US')

        if phone_number.phone_number is None:
            flash("Invalid Number")

        else:

            number = phone_number.phone_number

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

            flash("Thank you. We'll be in touch soon!")

        return redirect('/metar')


@app.route("/resume")
def resume():
    return render_template("resume.html")


@app.route("/admin")
def admin():
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    results = cur.execute("SELECT * FROM logs")

    # Retrieve query results
    records = cur.fetchall()

    print(f"results:{results}")
    print(f"records:{records}")

    return redirect("/")

@app.route("/<nickname>")
def short_url(nickname):
    #URL shortener

    print(f"short_url:{nickname}")
    return redirect("/")


@app.route("/pdf")
def pdf():
    return send_file('static/resume_TravisTurk_web.pdf', attachment_filename='resume.TravisTurk.pdf')


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
