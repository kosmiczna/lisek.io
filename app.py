# lisek.io


from flask import Flask, render_template, redirect
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from dotenv import load_dotenv
import json
import os
import subprocess
import time

load_dotenv()

app = Flask(__name__)


with open("links.json", "r") as file:
    links = json.load(file)

# simple in-memory cache so repeat visits don't hammer scoresaber/github's apis
_cache = {}

def cached(key, ttl, fetch):
    cached_result = _cache.get(key)
    if cached_result and time.time() - cached_result[1] < ttl:
        return cached_result[0]
    result = fetch()
    _cache[key] = (result, time.time())
    return result

GIT_HASH = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()

GITHUB_USER = "kosmiczna"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

# main page
@app.route("/")
def index():
    return render_template("index.html", git_hash=GIT_HASH)

# test endpoint for testing
@app.route("/dev")
def dev():
    return render_template("index2.html")

# scoresaber api "proxy", cached for 5 minutes
@app.route("/api/scoresaber")
def scoresaber():
    def fetch():
        req = Request("https://scoresaber.com/api/v2/players/76561199033653351", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as res:
            return res.read()
    try:
        return cached("scoresaber", 300, fetch), 200, {"Content-Type": "application/json"}
    except URLError as e:
        print("scoresaber api error:", e.read().decode() if isinstance(e, HTTPError) else e)
        return {"error": "scoresaber unavailable"}, 502

# github commits - using api w token, cached for 15 minutes
@app.route("/api/github")
def github():
    def fetch():
        query = """
        query($login: String!) {
            user(login: $login) {
                contributionsCollection {
                    contributionCalendar {
                        weeks {
                            contributionDays {
                                date
                                contributionCount
                            }
                        }
                    }
                }
                repositories(privacy: PUBLIC) {
                    totalCount
                }
            }
        }
        """
        body = json.dumps({"query": query, "variables": {"login": GITHUB_USER}}).encode()
        req = Request(
            "https://api.github.com/graphql",
            data=body,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json",
                "User-Agent": "lisek.io",
            },
        )
        with urlopen(req) as res:
            return res.read()
    try:
        return cached("github", 900, fetch), 200, {"Content-Type": "application/json"}
    except URLError as e:
        print("github api error:", e.read().decode() if isinstance(e, HTTPError) else e)
        return {"error": "github unavailable"}, 502

# url shortner
@app.route("/<link>")
def link(link):
    for entry in links:
        if link in entry:
            return redirect(entry[link])
    else:
        return "not found", 404

if __name__ == "__main__":
    app.run(port=5001, debug=os.environ.get("FLASK_DEBUG") == "1")
