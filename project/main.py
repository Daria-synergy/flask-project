from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app , db, render_as_batch=True)
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    uni = db.Column(db.String(64), nullable=False)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True, nullable=False)
    subtitle = db.Column(db.String(64), unique=True, nullable=False)
    text = db.Column(db.String(128), nullable=False)

@app.route('/')
def index():
    '''user = User(name="Ivan", email="ivan@ivanovich.com")
    db.session.add(user)
    db.session.commit()'''
    return render_template("index.html")

@app.route("/notes", methods=["post", "get"])
def notes():
    if request.method == 'POST':
        note = Notes(title=request.form["h"], subtitle=request.form["s"], text=request.form["name"])
        db.session.add(note)
        db.session.commit()
    n = Notes.query.all()
    return render_template("notes.html", n=n)

if __name__ == '__main__':
    app.run(debug=True)
