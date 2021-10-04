from flask import Flask, render_template, send_file, url_for, redirect, flash, request
from flask_session import Session
from twilio.twiml.messaging_response import MessagingResponse
import requests
from twilio.rest import Client
import os
import csv
import re

import threading
import discord
from dotenv import load_dotenv


# Flask App
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
messaging_service_sid='MGd24392f1df2b12a99eb4b85d2bdd4aec'
number_turk = os.getenv('NUMBER_TURK')
client = Client(account_sid, auth_token)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



def fetch_metar(airport):

    metars = requests.get('https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv')
    url_content = metars.content

    result = url_content

    csv_file = open('static/metars.csv', 'wb')
    csv_file.write(url_content)
    csv_file.close()

    with open('static/metars.csv', 'r') as csvfile:

        csv_reader = csv.reader(csvfile)

        header_found = False
        for row in csv_reader:

            if len(row) == 1:
                next(csv_reader)

            else:
                # Capture header if first time encoutering it
                if header_found == False:
                    header_found = True
                    headers = row

                else:
                    if row[1] == airport:
                        result = row[0]

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
    "time" : "⏳",
    "warning" : "⚠️"
    }

    print (wxkey)

    return (result)



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/portfolio")
def portfolio():
    flash("flashy message")
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

    print(message.sid)

    return redirect('/')


@app.route("/message", methods=['POST'])
def message():


    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    print(body)

    # Start our TwiML response
    resp = MessagingResponse()


    # TODO add STOP and SETTINGS
    keywords = ['HELP', 'METAR']



    if 'HELP' in body:
        resp.message(f'''
        OPTIONS\n
        {keywords}

        ''')

    if 'METAR' in body:
        airports = re.findall("K...", body)
        print(f"Found airports: {airports}")

        metar = fetch_metar(airports[0])
        resp.message(f"METAR {airports[0]}\n{metar}")        


    return str(resp)


@app.route("/message/status")
def message_status():

    # https://www.twilio.com/docs/sms/tutorials/how-to-confirm-delivery-python
    return redirect('/')



@app.route("/resume")
def resume():
    return render_template("resume.html")


@app.route("/pdf")
def pdf():
    return send_file('static/resume_TravisTurk_web.pdf', attachment_filename='resume.TravisTurk.pdf')


# # if __name__ == '__main__':
# #     app.run()

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
