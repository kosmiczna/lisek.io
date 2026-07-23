# lisek.io


from flask import Flask, render_template, redirect
from urllib.request import urlopen, Request
import json
import subprocess

app = Flask(__name__)


with open("links.json", "r") as file:
    links = json.load(file)

GIT_HASH = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()

# main page
@app.route("/")
def index():
    return render_template("index.html", git_hash=GIT_HASH)

# test endpoint for testing
@app.route("/dev")
def dev():
    return render_template("index2.html")

# scoresaber api "proxy"
@app.route("/api/scoresaber")
def scoresaber():
    req = Request("https://scoresaber.com/api/v2/players/76561199033653351", headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as res:
        return res.read(), 200, {"Content-Type": "application/json"}

# url shortner
@app.route("/<link>")
def link(link):
    for entry in links:
        if link in entry:
            return redirect(entry[link])
    else:
        return "not found", 404

if __name__ == "__main__":
    app.run(debug=True)
