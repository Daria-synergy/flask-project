from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'qwerty'
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    word = db.Column(db.String(256), nullable=False)  # Увеличен размер для хеша
    token = db.Column(db.String(32))
    token_expiration = db.Column(db.DateTime)  # Добавлено поле для срока действия токена

    def set_password(self, password):
        """Устанавливает хешированный пароль"""
        self.word = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль"""
        return check_password_hash(self.word, password)

    def generate_token(self):
        """Генерирует токен и устанавливает срок его действия"""
        self.token = secrets.token_hex(16)
        self.token_expiration = datetime.utcnow() + timedelta(minutes=30)
        return self.token


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True, nullable=False)
    subtitle = db.Column(db.String(64), unique=True, nullable=False)
    text = db.Column(db.String(128), nullable=False)


@app.route('/', methods=["GET", "POST"])
def home():
    '''user = User(name="Ivan", email="ivan@ivanovich.com")
    db.session.add(user)
    db.session.commit()'''
    return render_template("home.html")

@app.route('/register', methods=["post", "get"])
def reg():
    if request.method == "GET":
        return render_template("reg.html")
    else:
        # Создаём нового пользователя
        user = User(username=request.form["login"], email=request.form["email"])
        user.set_password(request.form["word"])  # Хешируем пароль
        user.generate_token()  # Генерируем токен

        db.session.add(user)
        db.session.commit()
        flash("Вы зарегистрированы")
        return redirect(url_for("login"))


@app.route('/login', methods=["post", "get"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = User.query.filter_by(username=request.form['login']).first()
        if user and user.check_password(request.form['word']):
            # Генерируем новый токен при входе
            token = user.generate_token()
            db.session.commit()  # Сохраняем токен в базе
            session["token"] = token  # Сохраняем токен в сессии
            session["user_id"] = user.id  # Сохраняем ID пользователя
            flash('Вы успешно вошли')
            return redirect(url_for("notes"))
        else:
            flash('Неверные данные')
            return render_template("login.html")


@app.before_request
def check_auth():
    # Список страниц, доступных без авторизации
    allowed_endpoints = ['login', 'reg', 'static', 'home']

    # Если запрос к разрешённой странице - пропускаем
    if request.endpoint in allowed_endpoints:
        return None

    # Получаем токен и ID пользователя из сессии
    token = session.get("token")
    user_id = session.get("user_id")

    if not token or not user_id:
        flash('Пожалуйста, войдите в систему')
        return redirect(url_for('home'))

    # Проверяем токен в базе данных
    user = User.query.filter_by(id=user_id, token=token).first()

    if not user:
        flash('Недействительный токен. Войдите заново')
        session.clear()
        return redirect(url_for('home'))

    # Проверяем срок действия токена
    if not user.token_expiration or datetime.utcnow() > user.token_expiration:
        flash('Срок действия сессии истёк. Войдите заново')
        session.clear()
        return redirect(url_for('home'))

    return None


@app.route("/logout")
def logout():
    session.clear()  # Очищаем всю сессию
    flash('Вы вышли из системы')
    return redirect(url_for('home'))


@app.route("/notes", methods=["post", "get"])
def notes():
    if request.method == 'POST':
        note = Notes(title=request.form["h"], subtitle=request.form["s"], text=request.form["name"])
        flash('Запись успешно добавлена')
        db.session.add(note)
        db.session.commit()
    n = Notes.query.all()
    return render_template("notes.html", n=n)

@app.route("/create", methods=["post", "get"])
def create():
    return render_template("create.html")

@app.route("/card/<c>")
def card(c):
    n = Notes.query.get(c)
    return render_template("card.html", n=n)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
if __name__ == '__main__':
    app.run(debug=True)
