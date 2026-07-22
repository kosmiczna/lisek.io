# lisek.io


from flask import Flask, render_template, redirect
import json

app = Flask(__name__)


with open("links.json", "r") as file:
    links = json.load(file)

# main page
@app.route("/")
def index():
    return render_template("index.html")

# url shortner
@app.route("/<link>")
def link(link):
    for entry in links:
        if link in entry:
            return redirect(entry[link])
    else:
        return "not found"

if __name__ == "__main__":
    app.run(debug=True)
