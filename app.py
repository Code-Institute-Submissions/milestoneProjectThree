# Import Libraries

import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash, safe_str_cmp

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
    return render_template("sign_up.html")



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
