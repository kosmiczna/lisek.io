# lisek.io

import json
import os
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from flask import Flask, redirect, render_template

load_dotenv()

app = Flask(__name__)

with open("links.json", "r") as file:
    links = json.load(file)

_cache = {}

def cached(key, ttl, fetch):
    cached_result = _cache.get(key)
    if cached_result and time.time() - cached_result[1] < ttl:
        return cached_result[0]
    result = fetch()
    _cache[key] = (result, time.time())
    return result

def proxy(name, ttl, fetch):
    try:
        return cached(name, ttl, fetch), 200, {"Content-Type": "application/json"}
    except URLError as e:
        print(f"{name} api error:", e.read().decode() if isinstance(e, HTTPError) else e)
        return {"error": f"{name} unavailable"}, 502

GIT_HASH = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()

GITHUB_USER = "kosmiczna"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

# main page
@app.route("/")
def index():
    return render_template("index.html", git_hash=GIT_HASH)

# scoresaber api "proxy", cached for 5 minutes
@app.route("/api/scoresaber")
def scoresaber():
    def fetch():
        req = Request("https://scoresaber.com/api/v2/players/76561199033653351", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as res:
            return res.read()
    return proxy("scoresaber", 300, fetch)

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
    return proxy("github", 900, fetch)

# url shortner
@app.route("/<link>")
def link(link):
    for entry in links:
        if link in entry:
            return redirect(entry[link])
    return "not found", 404

if __name__ == "__main__":
    app.run(port=5001, debug=os.environ.get("FLASK_DEBUG") == "1")
