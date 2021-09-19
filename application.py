from flask import Flask, render_template, send_file, url_for, redirect, flash

import os
import threading
import discord
from dotenv import load_dotenv


# Flask App
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/")
def home():
    # return redirect("/bio")
    return render_template("index.html")

@app.route("/portfolio")
def portfolio():
    return render_template("projects.html")

@app.route("/bio")
def bio():
    return render_template("bio.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/pdf")
def pdf():
    return send_file('static/resume_TravisTurk_web.pdf', attachment_filename='resume.TravisTurk.pdf')


# @app.route("/wx")
# def wx():
#     return render_template("wx.html")

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
