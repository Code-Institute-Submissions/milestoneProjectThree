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


# Default View
@app.route("/")
def default():
    return render_template("default.html")


# All Titles View
@app.route("/home/<username>")
def get_titles(username):
    # retrieve the session user's username from db for decorator
    # and flash messages, prevents users accessing other user resources
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find({"created_by": username}))
    title_count = mongo.db.titles.count_documents(
        {"created_by": username})
    if titles:
        flash("There are currently {} titles in your catalogue"
              .format(title_count))
    else:
        flash("There are currently no titles in your catalogue")

    return render_template("titles.html", titles=titles)


# Register View
@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":

        # store form inputs in variables
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
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
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": generate_password_hash(password)
            }
        mongo.db.users.insert_one(register)
        flash("Congratulations {}! You have registered successfully."
              .format(first_name.capitalize()))
        return redirect(url_for("sign_in"))

    return render_template("sign_up.html")


@app.route("/signin", methods=["GET", "POST"])
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
                first_name = mongo.db.users.find_one(
                    {"username": session["user"]})["first_name"].capitalize()
                flash("Welcome, {}".format(first_name))
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


@app.route("/userprofile/<username>", methods=["GET", "POST"])
def user_profile(username):
    # retrieve the session user's username from db
    # prevents users accessing other user resources
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"].capitalize()
    last_name = mongo.db.users.find_one(
        {"username": session["user"]})["last_name"].capitalize()
    # retrieve user collection counts from db
    library_count = mongo.db.libraries.count_documents(
        {"created_by": session["user"]})
    titles_count = mongo.db.titles.count_documents(
        {"created_by": session["user"]})
    return render_template(
                    "user_profile.html", username=username,
                    first_name=first_name, last_name=last_name,
                    library_count=library_count, titles_count=titles_count)


@app.route("/signout")
def sign_out():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("sign_in"))


# Get Individual Title Detail
@app.route('/home/detail/<title_id>')
def get_title_detail(title_id):
    title = mongo.db.titles.find_one({"_id": ObjectId(title_id)})
    return render_template("title_detail.html", title=title)


# Edit Title
@app.route('/home/edittitle')
def edit_title():
    
    return render_template("edit_title.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
