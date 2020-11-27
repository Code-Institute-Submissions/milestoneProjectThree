# Import Libraries

import os
import imdb
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
movieDB = imdb.IMDb()

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


# Add Title
@app.route('/home/addtitle', methods=["GET", "POST"])
def add_title():
    if request.method == "POST":
        is_watched = "on" if request.form.get("is_watched") else "off"
        is_bluray = "on" if request.form.get("is_bluray") else "off"
        title = {
            "library_name": request.form.get("library_name").lower(),
            "title_name": request.form.get("title_name").lower(),
            "release_year": request.form.get("release_year"),
            "description": request.form.get("description"),
            "genre": request.form.get("genre").lower(),
            "director": request.form.get("director").lower(),
            "cast": request.form.get("cast").lower(),
            "duration": request.form.get("duration"),
            "image_url": request.form.get("image_url"),
            "is_watched": is_watched,
            "is_bluray": is_bluray,
            "my_rating": request.form.get("rating"),
            "purchase_price": request.form.get("purchase_price"),
            "purchase_date": request.form.get("purchase_date"),
            "created_by": session["user"]
        }
        mongo.db.titles.insert_one(title)
        flash("Title Successfully Added")
        return redirect(url_for("get_titles", username=session['user']))

    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("add_title.html", libraries=libraries)


# Edit Title
@app.route("/home/edittitle/<title_id>", methods=["GET", "POST"])
def edit_title(title_id):
    if request.method == "POST":
        is_watched = "on" if request.form.get("is_watched") else "off"
        is_bluray = "on" if request.form.get("is_bluray") else "off"
        submit = {
            "library_name": request.form.get("library_name").lower(),
            "title_name": request.form.get("title_name").lower(),
            "release_year": request.form.get("release_year"),
            "description": request.form.get("description"),
            "genre": request.form.get("genre").lower(),
            "director": request.form.get("director").lower(),
            "cast": request.form.get("cast").lower(),
            "duration": request.form.get("duration"),
            "image_url": request.form.get("image_url"),
            "is_watched": is_watched,
            "is_bluray": is_bluray,
            "my_rating": request.form.get("rating"),
            "purchase_price": request.form.get("purchase_price"),
            "purchase_date": request.form.get("purchase_date"),
            "created_by": session["user"]
        }
        mongo.db.titles.update({"_id": ObjectId(title_id)}, submit)
        flash("Title Successfully Updated")

    title = mongo.db.titles.find_one({"_id": ObjectId(title_id)})
    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("edit_title.html", title=title, libraries=libraries)


# Delete Title
@app.route("/deletetitle/<title_id>")
def delete_title(title_id):
    mongo.db.titles.remove({"_id": ObjectId(title_id)})
    flash("Title Successfully Deleted")
    return redirect(url_for("get_titles", username=session['user']))


@app.route("/getlibraries/<username>")
def get_libraries(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    libraries = list(mongo.db.libraries.find(
        {"created_by": username}).sort("library_name", 1))
    library_count = mongo.db.libraries.count_documents(
        {"created_by": username})
    if library_count == 1:
        flash("There is currently {} collection in your catalogue"
              .format(library_count))
    elif library_count > 1:
        flash("There are currently {} collections in your catalogue"
              .format(library_count))
    else:
        flash("There are currently no collections in your catalogue")

    return render_template("libraries.html", libraries=libraries)


@app.route("/addlibrary", methods=["GET", "POST"])
def add_library():
    if request.method == "POST":
        library = {
            "library_name": request.form.get("library_name").lower(),
            "created_by": session["user"]
        }
        mongo.db.libraries.insert_one(library)
        flash("New Collection Added")
        return redirect(url_for("get_libraries", username=session['user']))

    return render_template("add_library.html")


@app.route("/editlibrary/<library_id>", methods=["GET", "POST"])
def edit_library(library_id):
    if request.method == "POST":
        submit = {
            "library_name": request.form.get("library_name").lower(),
            "created_by": session["user"]
        }
        mongo.db.libraries.update({"_id": ObjectId(library_id)}, submit)
        flash("Collection Successfully Updated")
        return redirect(url_for("get_libraries", username=session['user']))

    library = mongo.db.libraries.find_one({"_id": ObjectId(library_id)})
    return render_template("edit_library.html", library=library)


@app.route("/deletelibrary/<library_id>")
def delete_library(library_id):
    mongo.db.libraries.remove({"_id": ObjectId(library_id)})
    flash("Collection Successfully Deleted")
    return redirect(url_for("get_libraries", username=session['user']))


@app.route("/search", methods=["GET", "POST"])
def search():
    querytop = request.form.get("search-topnav")
    queryside = request.form.get("search-sidenav")
    if querytop:
        titles = list(mongo.db.titles.find(
            {'$and': [{"$text": {"$search": querytop}},
                      {"created_by": session["user"]}]}))
    else:
        titles = list(mongo.db.titles.find(
            {'$and': [{"$text": {"$search": queryside}},
                      {"created_by": session["user"]}]}))
    if len(titles) == 0:
        flash("There are no results for your search")

    return render_template("titles.html", titles=titles)


@app.route("/imdbsearch")
def imdb_search():
    form_test = "Papillon"
    # movie_list = movieDB.search_movie(title_name)
    # flash("Searching IMDb Database for the following: {} "
    #       .format(title_name).title())

    movie_list = movieDB.search_movie(form_test)
    flash("Searching IMDb Database for the following: {} "
          .format(form_test).title())

    return render_template("imdb_search.html", movie_list=movie_list)


@app.route("/imdbformupdate/<movie_id>")
def imdb_form_update(movie_id):
    # movie_id = movie_id
    movieDB_title = movieDB.get_movie(movie_id)
    movie_details_all = movieDB.get_movie_main(movie_id)
    # movieDB_title = movie_details_all['data']['title']
    # movieDB_year = movie_details_all['data']['year']
    # movieDB_plot = movie_details_all['data']['plot outline']
    # movieDB_genres = movie_details_all['data']['genres']
    # movieDB_directors = movie_details_all['data']['directors']
    # movieDB_stars = movie_details_all['data']['cast'][:3:]
    # movieDB_duration = movie_details_all['data']['runtimes']
    # movieDB_img_url = movie_details_all['data']['cover url']
    moviedict = {
        "title_name":  movieDB_title,
        "release_year": movie_details_all['data']['year'],
        "description": movie_details_all['data']['plot outline'],
        "genres": movie_details_all['data']['genres'],
        "directors": movie_details_all['data']['directors'],
        "cast": movie_details_all['data']['cast'][:3:],
        "duration": movie_details_all['data']['runtimes'],
        "image_url": movie_details_all['data']['cover url']
    }

    flash("IMDb Database for: {} ".format(movieDB_title))
    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("imdb_form_update.html", libraries=libraries,
                           moviedict=moviedict)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
