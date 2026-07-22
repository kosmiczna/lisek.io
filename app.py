# lisek.io


from flask import Flask, render_template

app = Flask(__name__)


# main page
@app.route("/")
def index():
    return render_template("index.html")

# url shortner
@app.route("/<link>")
def link(link):
    return link

if __name__ == "__main__":
    app.run(debug=True)
