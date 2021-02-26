from flask import Flask, render_template, send_file

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/pdf")
def pdf():
    return send_file('static/resume_TravisTurk_web.pdf', attachment_filename='resume.TravisTurk.pdf') 

@app.route("/contact")
def contact():
    return render_template("contact.html")

# # if __name__ == '__main__':
# #     app.run()