from flask import request, render_template, redirect, url_for, session, make_response, flash
from app import app
from app.forms import LoginForm
import json
import datetime

with open("users.json", "r") as file:
    users = json.load(file)

@app.route("/")
def index():
    form = LoginForm()
    return render_template("login.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users and users[username] == password:
            session["username"] = username

            if form.remember.data:
                session.permanent = True

            flash('Ви успішно увійшли!', 'success')
            return redirect(url_for("info"))

        flash('Неправильне ім\'я користувача або пароль.', 'error')

    return render_template("login.html", form=form)

@app.route("/info", methods=["GET", "POST"])
def info():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    cookies = request.cookies.items()
    form = LoginForm()  # Ініціалізуємо форму

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_cookie":
            key = request.form.get("key")
            value = request.form.get("value")
            expiration_time = request.form.get("expiration_time")

            if key and value and expiration_time:
                expiration_time = int(expiration_time)
                expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=expiration_time)
                response = make_response(render_template("info.html", username=username, cookies=cookies, form=form))
                response.set_cookie(key, value, expires=expiration_date)
                message = f"Cookie '{key}' додано успішно."
                return response
            else:
                message = "Будь ласка, заповніть всі поля."

    return render_template("info.html", username=username, cookies=cookies, form=form)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/change_password", methods=["POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    new_password = request.form.get("new_password")

    users[username] = new_password

    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

    message = "Пароль змінено успішно."
    return render_template("info.html", username=username, message=message, cookies=request.cookies.items())
