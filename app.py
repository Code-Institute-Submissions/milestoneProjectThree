# Import Libraries

import os
import imdb
import string

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


############################################################
# Search Functions
############################################################

# Navbar Search View
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("search")
    if query:
        titles = list(mongo.db.titles.find(
            {'$and': [{"$text": {"$search": query}},
                      {"created_by": session["user"]}]}))

    if len(titles) == 0:
        flash("There are no results for your search")

    return render_template("titles.html", titles=titles)


# Deserialised imdbPY get & formatting functions
# Retrieve and format imdb plot summary from array of plot details
def get_formatted_plot_summary(title_obj):
    if title_obj.get('plot'):
        plot_summary_and_notes_array = title_obj.get('plot')[0].split('::')
        plot_summary_only = plot_summary_and_notes_array[0]
        return plot_summary_only


# Retrieve and format imdb directors details
def get_formatted_directors(title_obj):
    directors_string = ""
    if title_obj.get('directors'):
        for director in title_obj.get('directors')[:5]:
            directors_string += director['name'] + ', '
        directors_string = directors_string[:-2]
        return directors_string


# Retrieve and format imdb star details
def get_formatted_stars(title_obj):
    stars_string = ""
    if title_obj.get('cast'):
        for star in title_obj.get('cast')[:6]:
            stars_string += star['name'] + ', '
        stars_string = stars_string[:-2]
        return stars_string


# Retrieve and format imdb genres details
def get_formatted_genres(title_obj):
    genres_string = ""
    if title_obj.get('genres'):
        for genre in title_obj.get('genres'):
            genres_string += genre + ", "
        genres_string = genres_string[:-2]
        return genres_string


# Retrieve and format imdb runtime details
def get_title_duration(title_obj):
    if title_obj.get('runtime'):
        return title_obj.get('runtimes')[0]


############################################################
# Basic Views
############################################################

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
    titles = list(mongo.db.titles.find(
        {"created_by": username}).sort("title_name", 1))
    title_count = mongo.db.titles.count_documents(
        {"created_by": username})

    if title_count == 1:
        flash("There is currently {} title in your catalogue"
              .format(title_count))
    elif title_count > 1:
        flash("There are currently {} titles in your catalogue"
              .format(title_count))
    else:
        flash("There are currently no titles in your catalogue")

    return render_template("titles.html", titles=titles)


# Get Individual Title Detail
@app.route('/home/detail/<title_id>')
def get_title_detail(title_id):
    title = mongo.db.titles.find_one({"_id": ObjectId(title_id)})
    return render_template("title_detail.html", title=title)


############################################################
# Authentication Views
############################################################

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


# Login view
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


# Logout View
@app.route("/signout")
def sign_out():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("sign_in"))


# User profile view
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


############################################################
# Filter Views
############################################################
# Collections/Library Filters
############################################################
# Display Collections/Libraries
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


# Filter Collection/Library View
@app.route("/libraries/<library_name>/<username>/")
def filter_library_titles(library_name, username):
    # retrieve the session user's username from db for decorator
    # and flash messages, prevents users accessing other user resources
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find(
                    {'$and': [{"library_name": library_name},
                     {"created_by": username}]}))
    title_count = mongo.db.titles.count_documents(
        {'$and': [{"library_name": library_name},
                  {"created_by": username}]})

    if title_count == 1:
        flash("There is currently {} title in this collection"
              .format(title_count))
    elif title_count > 1:
        flash("There are currently {} titles in this collection"
              .format(title_count))
    else:
        flash("There are currently no titles in this collection")

    return render_template("filter_library_titles.html",
                           titles=titles, library_name=library_name)


############################################################
# Genre Filters
############################################################

# Deserialised functions for genre and dircetors filters
# From String library punctuation removal
def remove_punc(string_var):
    # exclude = set(string.punctuation)
    table = str.maketrans(dict.fromkeys(string.punctuation))
    return string_var.translate(table)


# Clean Genre String function
def clean_genres(string_in):
    string_in = remove_punc(string_in)[:-1]
    string_in = string_in.replace("  ", " ").replace("  ", " ")
    string_in = string_in.replace("scifi", "sci-fi ")
    string_in = string_in.split(" ")
    string_in = list(dict.fromkeys(string_in))
    return string_in


# Display Genres
@app.route("/getgenres/<username>")
def get_genres(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find({"created_by": username}))

    genres = ""
    for title in titles:
        genres += title['genre'] + ' '

    genres = clean_genres(genres)
    genres_count = len(genres)

    if genres_count == 1:
        flash("There is currently {} genre in your catalogue"
              .format(genres_count))
    elif genres_count > 1:
        flash("There are currently {} genres in your catalogue"
              .format(genres_count))
    else:
        flash("There are currently no genres in your catalogue")

    return render_template("genres.html", titles=titles, genres=genres)


# Filter Genre View
@app.route("/genres/<genre_name>/<username>/")
def filter_genre_titles(genre_name, username):

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find(
                    {'$and': [{"$text": {"$search": genre_name}},
                     {"created_by": username}]}))
    title_count = mongo.db.titles.count_documents(
                    {'$and': [{"$text": {"$search": genre_name}},
                     {"created_by": username}]})
    if title_count == 1:
        flash("There is currently {} title in this Genre"
              .format(title_count))
    elif title_count > 1:
        flash("There are currently {} titles in this Genre"
              .format(title_count))
    else:
        flash("There are currently no titles in this Genre")

    return render_template("filter_genre_titles.html",
                           titles=titles, genre_name=genre_name)


############################################################
# Director Filters
############################################################

# Clean Directors String function
def clean_directors(string_in):
    string_in = string_in.replace(", , ", ", ").replace(", , ", ", ")[:-2]
    string_in = string_in.split(", ")
    string_in = list(dict.fromkeys(string_in))
    return string_in


# Display Directors View
@app.route("/getdirectors/<username>")
def get_directors(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find({"created_by": username}))

    directors = ""
    for title in titles:
        directors += title['director'] + ', '

    directors = clean_directors(directors)
    directors_count = len(directors)

    if directors_count == 1:
        flash("There is currently {} director in your catalogue"
              .format(directors_count))
    elif directors_count > 1:
        flash("There are currently {} directors in your catalogue"
              .format(directors_count))
    else:
        flash("There are currently no directors in your catalogue")

    return render_template(
        "directors.html", titles=titles, directors=directors)


# Filter Directors View
@app.route("/directors/<director_name>/<username>/")
def filter_director_titles(director_name, username):

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find(
                    {'$and': [{"$text": {"$search": director_name}},
                     {"created_by": username}]}))
    title_count = mongo.db.titles.count_documents(
                    {'$and': [{"$text": {"$search": director_name}},
                     {"created_by": username}]})
    if title_count == 1:
        flash("There is currently {} title for this Director"
              .format(title_count))
    elif title_count > 1:
        flash("There are currently {} titles for this Director"
              .format(title_count))
    else:
        flash("There are currently no titles for this Director")

    return render_template("filter_director_titles.html",
                           titles=titles, director_name=director_name)


############################################################
# Releazse Year Filters
############################################################

# Clean Directors String function
def clean_years(string_in):
    # string_in = string_in.replace(", , ", ", ")[:-2]
    string_in = string_in.split(", ")[:-2]
    string_in = list(dict.fromkeys(string_in))
    return string_in


# Display Years View
@app.route("/getyears/<username>")
def get_years(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find({"created_by": username}))

    years = ""
    for title in titles:
        years += title['release_year'] + ', '

    years = clean_years(years)
    years_count = len(years)

    if years_count == 1:
        flash("Catalogue titles are currently grouped in a single year")
    elif years_count > 1:
        flash("Catalogue titles are currently grouped across {} years"
              .format(years_count))
    else:
        flash("""There are currently no titles
               grouped by year in your catalogue""")

    return render_template(
        "years.html", titles=titles, years=years)


# Filter Release Year View
@app.route("/years/<release_year>/<username>/")
def filter_year_titles(release_year, username):

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    titles = list(mongo.db.titles.find(
                    {'$and': [{"release_year": release_year},
                     {"created_by": username}]}))
    # title_count = mongo.db.titles.count_documents(
    #                 {'$and': [{"release_year": release_year},
    #                  {"created_by": username}]})
    # if title_count == 1:
    #     flash("There is currently {} title for this Director"
    #           .format(title_count))
    # elif title_count > 1:
    #     flash("There are currently {} titles for this Director"
    #           .format(title_count))
    # else:
    #     flash("There are currently no titles for this Director")

    return render_template("filter_year_titles.html",
                           titles=titles, release_year=release_year)


############################################################
# Add/Delete Title Views
############################################################

# Add Title
@app.route('/home/addtitle', methods=["GET", "POST"])
def add_title():
    if request.method == "POST":
        if 'add_title_btn' in request.form:
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

        elif 'imdb_search_btn' in request.form:
            text_search = request.form.get("title_name").lower()
            title_list = movieDB.search_movie(text_search)
            library_name = request.form.get("library_name").lower()
            flash("Searching IMDb Database for the following: {} "
                  .format(text_search).title())

            return render_template(
                "add_imdb_search.html", title_list=title_list,
                library_name=library_name
                )

    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("add_title.html", libraries=libraries)


# IMDB form update for add title view
@app.route("/addimdbformupdate/<library_selected>/<movieDB_id>")
def add_imdb_form_update(movieDB_id, library_selected):
    title_obj = movieDB.get_movie(movieDB_id)
    movieDB_name = title_obj.get('title')
    title_dict = {
        "title_name":  movieDB_name,
        "release_year": title_obj.get('year'),
        "title_type ": title_obj.get('kind'),
        "description":  get_formatted_plot_summary(title_obj),
        "genres": get_formatted_genres(title_obj),
        "directors": get_formatted_directors(title_obj),
        "cast": get_formatted_stars(title_obj),
        "duration": get_title_duration(title_obj),
        "image_url": title_obj.get('full-size cover url')
    }

    flash("IMDb Database for: {} ".format(movieDB_name))
    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("add_imdb_form_update.html", libraries=libraries,
                           title_dict=title_dict,
                           library_selected=library_selected)


# Delete Title
@app.route("/deletetitle/<title_id>")
def delete_title(title_id):
    mongo.db.titles.remove({"_id": ObjectId(title_id)})
    flash("Title Successfully Deleted")
    return redirect(url_for("get_titles", username=session['user']))


############################################################
# Edit Title Views
############################################################

# Edit Title
@app.route("/home/edittitle/<title_id>", methods=["GET", "POST"])
def edit_title(title_id):
    if request.method == "POST":
        if 'edit_title_btn' in request.form:
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

        elif 'imdb_search_btn' in request.form:
            text_search = request.form.get("title_name").lower()
            title_list = movieDB.search_movie(text_search)
            flash("Searching IMDb Database for the following: {} "
                  .format(text_search).title())

            return render_template("edit_imdb_search.html",
                                   title_list=title_list,
                                   title_id=title_id)

    title = mongo.db.titles.find_one({"_id": ObjectId(title_id)})
    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("edit_title.html",
                           title=title, libraries=libraries)


# IMDB form update for edit title view
@app.route("/editimdbformupdate/<title_id>/<movieDB_id>")
def edit_imdb_form_update(title_id, movieDB_id):
    title_obj = movieDB.get_movie(movieDB_id)
    movieDB_name = title_obj.get('title')
    title_dict = {
        "title_name":  movieDB_name,
        "release_year": title_obj.get('year'),
        "title_type ": title_obj.get('kind'),
        "description":  get_formatted_plot_summary(title_obj),
        "genres": get_formatted_genres(title_obj),
        "directors": get_formatted_directors(title_obj),
        "cast": get_formatted_stars(title_obj),
        "duration": get_title_duration(title_obj),
        "image_url": title_obj.get('full-size cover url')
    }

    if request.method == "POST":
        if 'edit_title_btn' in request.form:
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

        elif 'imdb_search_btn' in request.form:
            text_search = request.form.get("title_name").lower()
            title_list = movieDB.search_movie(text_search)
            flash("Searching IMDb Database for the following: {} "
                  .format(text_search).title())

            return render_template("edit_imdb_search.html",
                                   title_list=title_list,
                                   title_id=title_id)

    flash("IMDb Database for: {} ".format(movieDB_name))
    title = mongo.db.titles.find_one({"_id": ObjectId(title_id)})
    libraries = mongo.db.libraries.find(
        {"created_by": session["user"]}).sort("library_name", 1)
    return render_template("edit_imdb_form_update.html", libraries=libraries,
                           title_dict=title_dict,
                           title=title)


############################################################
# Collection/Library Views
# Note* variable named library to distinguish between
# App collection and mongoDB collection
############################################################

# Manage Collections/Libraries
@app.route("/managelibraries/<username>")
def manage_libraries(username):
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

    return render_template("manage_libraries.html", libraries=libraries)


# Add Collection/Library
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


# Edit Collection/Library
@app.route("/editlibrary/<library_id>", methods=["GET", "POST"])
def edit_library(library_id):
    if request.method == "POST":
        submit = {
            "library_name": request.form.get("library_name").lower(),
            "created_by": session["user"]
        }
        mongo.db.libraries.update({"_id": ObjectId(library_id)}, submit)
        flash("Collection Successfully Updated")
        return redirect(url_for("manage_libraries", username=session['user']))

    library = mongo.db.libraries.find_one({"_id": ObjectId(library_id)})
    return render_template("edit_library.html", library=library)


# Delete Collection/Library
@app.route("/deletelibrary/<library_id>")
def delete_library(library_id):
    mongo.db.libraries.remove({"_id": ObjectId(library_id)})
    flash("Collection Successfully Deleted")
    return redirect(url_for("manage_libraries", username=session['user']))


############################################################
# Environmental variables
############################################################

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)


############################################################
# Error Views
############################################################
