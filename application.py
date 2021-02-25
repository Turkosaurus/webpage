from flask import Flask, render_template

app = Flask(__name__)

# # Ensure templates are auto-reloaded
# app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/bio")
def index():
    return render_template("bio.html")

@app.route("/projects")
def index():
    return render_template("projects.html")

@app.route("/projects")
def index():
    return render_template("projects.html")



# if __name__ == '__main__':
#     app.run()