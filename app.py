import calendar_support as cals
import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, allowed_file, login_required

app = Flask(__name__)

# Ensure templates are auto-reloaded (CS50 staff)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies) (CS50 staff)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure session to upload files to the calendars folder
app.config["UPLOAD_FOLDER"] = "calendars"

# Configure CS50 Library to use SQLite database (CS50 staff)
db = SQL("sqlite:///project.db")


@app.route("/")
def homepage():
    """A simple homepage"""
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pw_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User submitted information via POST
    if request.method == "POST":

        # Ensure user submitted a username
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        
        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        
        # Ensure password was submitted
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Query database for user
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Return error messge if username already exists
        if len(rows) > 0:
            return apology("username already exists")
        
        # Hash the password
        p_hash = generate_password_hash(request.form.get("password"))
        
        # Insert new username and password into user database
        db.execute("INSERT INTO users (username, pw_hash) VALUES (?, ?)", request.form.get("username"), p_hash)

        # Redirect the user to the login page
        return redirect("/login")

    # If the user reached the route via GET
    else:
        return render_template("register.html")


@app.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():
    """Allow user to signal they want to schedule an event"""

    # User submitted information via POST
    if request.method == "POST":
        
        # Ensure user submitted a username
        if not request.form.get("other-user"):
            return apology("must provide someone's username", 400)

        # Ensure the username exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("other-user"))
        if len(rows) != 1:
            return apology("must provide a valid username", 400)

        # Calculate hash from usernames and update permissions table
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        other_user = request.form.get("other-user")
        pair_hash = hash("".join(sorted([username, other_user])))
        rows = db.execute("SELECT * FROM pairs WHERE hash = ?", pair_hash)
        if len(rows) == 0:
            db.execute("INSERT INTO pairs (user1, user2, hash) VALUES (?, ?, ?)", )
        user_no = 'user1' if username < other_user else 'user2'
        db.execute("UPDATE pairs SET ? = 1 WHERE hash = ?", user_no, pair_hash)

        # Continue scheduling if both users have allowed it
        row = db.execute("SELECT * FROM pairs WHERE hash = ?", pair_hash)[0]
        if row["user1"] == 1 and row["user2"] == 1:
            session[pair_hash] = True
            return redirect(url_for("scheduling", pair_hash=pair_hash))
        else:
            session[pair_hash] = False
            return redirect("/scheduling")

    # If the user reached the route via GET
    else:
        return render_template("schedule.html")


@app.route("/scheduling", methods=["GET", "POST"])
@login_required
def scheduling():
    """Continue to schedule an event"""

    # User submitted information via POST
    if request.method == "POST":

        if request.args.get("users"):
            users = request.args.get("users")
            if True:
                return render_template("scheduling.html", permission=True)
        
        # Ensure user submitted a username
        if not request.form.get("other-user"):
            return apology("must provide someone's username", 400)

        # Ensure the username exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("other-user"))
        if len(rows) != 1:
            return apology("must provide a valid username", 400)

        # Calculate hash from usernames and update permissions table
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        other_user = request.form.get("other-user")
        pair_hash = hash("".join(sorted([username, other_user])))
        rows = db.execute("SELECT * FROM pairs WHERE hash = ?", pair_hash)
        if len(rows) == 0:
            db.execute("INSERT INTO pairs (user1, user2, hash) VALUES (?, ?, ?)", 0, 0, pair_hash)
        user_no = 'user1' if username < other_user else 'user2'
        db.execute("UPDATE pairs SET ? = 1 WHERE hash = ?", user_no, pair_hash)

        # Continue scheduling if both users have allowed it
        row = db.execute("SELECT * FROM pairs WHERE hash = ?", pair_hash)[0]
        if row["user1"] == 1 and row["user2"] == 1:
            return redirect("/scheduling")
        else:
            return redirect("/")

    # If the user reached the route via GET
    else:
        return render_template("scheduling.html", permission=False)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """
    Allow user to upload an ics file, using the pattern shown in
    https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    """

    # User submitted information via POST
    if request.method == "POST":
        
        # Ensure a file was part of the POST request
        if "calendar" not in request.files:
            return apology("no file found", 400)

        # Ensure a file was uploaded
        calendar = request.files["calendar"]
        if calendar.filename == "":
            return apology("must upload a file", 400)

        # Ensure the file is an ics file
        if not allowed_file(calendar.filename):
            return apology("must upload iCalendar file", 400)

        # Rename and save the file
        if calendar:
            row = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]
            filename = row["username"] + ".ics"
            calendar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        return redirect("/")

    # If the user reached the route via GET
    else:
        return render_template("upload.html")
