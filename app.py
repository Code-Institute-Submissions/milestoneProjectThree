# Import Libraries

import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# Set links to environmental variables

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# All Titles View
@app.route("/")
@app.route("/get_titles")
def get_titles():
    titles = mongo.db.titles.find()
    return render_template("titles.html", titles=titles)


# Register View
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":

        # store form inputs in variables
        username = request.form.get("username")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirm-password")

        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": username.lower()})

        if existing_user:
            flash('Username already exists. Please Try again?')
            return redirect(url_for("sign_up"))

        # confirm password
        if password != confirmpassword:
            flash("Passwords do not match, please re-enter")
            return redirect(url_for("sign_up"))

        # register user to mongodb
        register = {
                "username": username,
                "password": generate_password_hash(password)
            }
        mongo.db.users.insert_one(register)
        flash("Congratulations!You have registered successfully.")
        return redirect(url_for("user_profile"))

    return render_template("sign_up.html")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": username.lower()})
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], password):
                session["user"] = username.lower()
                flash("Welcome, {}".format(username))
                return redirect(url_for(
                    "user_profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("sign_in"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("sign_in"))

    return render_template("sign_in.html")


@app.route("/user_profile/<username>", methods=["GET", "POST"])
def user_profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    # grab user collection counts from db
    library_count = mongo.db.libraries.count({"created_by": session["user"]})
    titles_count = mongo.db.titles.count({"created_by": session["user"]})
    # flash("Library & Titles Count, {}, {}".format(library_count, titles_count))
    return render_template(
                    "user_profile.html", username=username,
                    library_count=library_count, titles_count=titles_count)


@app.route("/sign_out")
def sign_out():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("sign_in"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
