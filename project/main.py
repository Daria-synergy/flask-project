from flask import Flask, render_template, request

app = Flask(__name__)
note = {}
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hello")
def hello():
    return 'Hello!'

@app.route("/hello/<name>")
def greetings(name):
    return f"Привет, {name}!"

'''@app.route("/submit", methods=["post"])
def submit():
    name = request.form["name"]
    return f"Привет, {name}!"'''

@app.route("/notes", methods=["post", "get"])
def notes():
    global note
    if request.method == 'POST':
        note[request.form["h"]] = request.form["name"]
    return render_template("notes.html", note=note)

'''@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404'''
if __name__ == "__main__":
    app.run(debug=True)
