"""
============================================================
 GENERIC FLASK CRUD APP — adapt this on exam day
============================================================
Structure (copy this shape for every entity the real spec asks for):

    @app.route("/x", methods=["GET", "POST"])   <- list page + add form
    def x():
        if login_required(): return redirect(...)
        if request.method == "POST":            <- CREATE
            ...read form fields...
            add_x(...)
            return redirect(url_for("x"))
        all_x = get_all_x()                      <- READ
        return render_template("x.html", items=all_x)

    @app.route("/x/edit/<int:xID>", methods=["POST"])
    def edit_x(xID):                              <- UPDATE
        if login_required(): return redirect(...)
        ...read form fields...
        update_x(xID, ...)
        return redirect(url_for("x"))

    @app.route("/x/delete/<int:xID>")
    def delete_x_route(xID):                      <- DELETE
        if login_required(): return redirect(...)
        delete_x(xID)
        return redirect(url_for("x"))

HOW TO ADAPT ON TEST DAY:
  1. Rename dbhelper import list to match your renamed dbhelper.py functions.
  2. Rename routes/URLs (/group -> /events, /person -> /participants, etc).
  3. Rename form field names to match the real <input name="..."> in your HTML.
  4. The computed-fee logic lives in entry()/register() below — that's
     usually the one part of the exam with real logic, so read it carefully.
============================================================
"""
from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import webbrowser
import os
import threading
from dbhelper import (
    init_database,
    add_group, get_all_groups, get_group, update_group, delete_group,
    add_person, get_all_persons, get_person, update_person, delete_person,
    add_entry, get_all_entries, get_entries_joined,
    add_user, get_all_users, get_user_by_id, get_user_by_username, get_user_by_email,
    update_user, update_user_password, delete_user,
)

app = Flask(__name__)
app.secret_key = "change-me-but-doesnt-matter-for-exam"
init_database()

# ============================================================
# SITE NAME — change THIS ONE LINE on exam day to match whatever
# system name they give you. Every template (navbar + login banner)
# pulls from this automatically — you never have to hunt through
# individual HTML files to rename the system.
# ============================================================
SITE_NAME = "Library System"

@app.context_processor
def inject_site_name():
    """Makes {{ SITE_NAME }} available in every template automatically,
    without having to pass it manually in every render_template() call."""
    return dict(SITE_NAME=SITE_NAME)


def login_required():
    """Returns True if nobody is logged in. Used at the top of every protected route."""
    return 'user_id' not in session


# ============================================================
# HOME — auto-redirect so the server always opens on a real page
# ============================================================
@app.route("/")
def home():
    if login_required():
        return redirect(url_for('login'))
    return redirect(url_for('group_page'))


# ============================================================
# LOGIN / LOGOUT / REGISTER
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = get_user_by_username(username)
        if user and check_password_hash(user["password"], password):
            session['user_id'] = user["userID"]
            session['username'] = user["username"]
            return redirect(url_for('group_page'))

        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new account. Public — no login required to reach this page."""
    if request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if not all([firstName, lastName, email, username, password]):
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        if get_user_by_username(username):
            flash("That username is already taken.", "error")
            return redirect(url_for('register'))

        if get_user_by_email(email):
            flash("That email is already registered.", "error")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        add_user(username, password_hash, firstName, lastName, email)
        flash("Account created! You can log in now.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


# ============================================================
# ACCOUNT — the logged-in user's own profile (Read / Update / Delete)
# ============================================================
@app.route("/account")
def account():
    if login_required():
        return redirect(url_for('login'))

    current_user = get_user_by_id(session['user_id'])
    return render_template("account.html", user=current_user)


@app.route("/account/edit", methods=["POST"])
def edit_account():
    if login_required():
        return redirect(url_for('login'))

    userID = session['user_id']
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")
    email = request.form.get("email")
    username = request.form.get("username")
    new_password = request.form.get("password")  # optional — may be left blank

    update_user(userID, firstName, lastName, email, username)

    # Only touch the password if the user actually typed a new one.
    if new_password and new_password.strip():
        update_user_password(userID, generate_password_hash(new_password))

    session['username'] = username  # keep session in sync if username changed
    flash("Account updated.", "success")
    return redirect(url_for('account'))


@app.route("/account/delete")
def delete_account():
    if login_required():
        return redirect(url_for('login'))

    delete_user(session['user_id'])
    session.clear()
    flash("Account deleted.", "success")
    return redirect(url_for('login'))


# ============================================================
# 1. GROUP — full CRUD (rename to your 1st master entity)
# ============================================================
@app.route("/group", methods=["GET", "POST"])
def group_page():
    if login_required():
        return redirect(url_for('login'))

    if request.method == "POST":
        groupName = request.form.get("groupName")
        groupDate = request.form.get("groupDate")
        groupPlace = request.form.get("groupPlace")
        groupFee = request.form.get("groupFee")
        add_group(groupName, groupDate, groupPlace, groupFee)
        flash("Added successfully.", "success")
        return redirect(url_for('group_page'))

    search = request.args.get("search", "").lower()
    all_groups = get_all_groups()
    if search:
        all_groups = [g for g in all_groups if search in g["groupName"].lower()]

    return render_template("group.html", groups=all_groups)


@app.route("/group/edit/<int:groupID>", methods=["POST"])
def edit_group(groupID):
    if login_required():
        return redirect(url_for('login'))

    groupName = request.form.get("groupName")
    groupDate = request.form.get("groupDate")
    groupPlace = request.form.get("groupPlace")
    groupFee = request.form.get("groupFee")
    update_group(groupID, groupName, groupDate, groupPlace, groupFee)
    flash("Updated successfully.", "success")
    return redirect(url_for('group_page'))


@app.route("/group/delete/<int:groupID>")
def delete_group_route(groupID):
    if login_required():
        return redirect(url_for('login'))

    delete_group(groupID)
    flash("Deleted successfully.", "success")
    return redirect(url_for('group_page'))


# ============================================================
# 2. PERSON — full CRUD (rename to your 2nd entity, has a Foreign Key)
# ============================================================
@app.route("/person", methods=["GET", "POST"])
def person_page():
    if login_required():
        return redirect(url_for('login'))

    if request.method == "POST":
        groupID = request.form.get("groupID")
        personFName = request.form.get("personFName")
        personLName = request.form.get("personLName")
        personRate = request.form.get("personRate")
        add_person(groupID, personFName, personLName, personRate)
        flash("Added successfully.", "success")
        return redirect(url_for('person_page'))

    search = request.args.get("search", "").lower()
    all_persons = get_all_persons()
    if search:
        all_persons = [p for p in all_persons if search in p["personFName"].lower()
                       or search in p["personLName"].lower()]

    # Dropdown needs the list of groups too, so the add/edit form can pick a groupID
    all_groups = get_all_groups()
    return render_template("person.html", persons=all_persons, groups=all_groups)


@app.route("/person/edit/<int:personID>", methods=["POST"])
def edit_person(personID):
    if login_required():
        return redirect(url_for('login'))

    groupID = request.form.get("groupID")
    personFName = request.form.get("personFName")
    personLName = request.form.get("personLName")
    personRate = request.form.get("personRate")
    update_person(personID, groupID, personFName, personLName, personRate)
    flash("Updated successfully.", "success")
    return redirect(url_for('person_page'))


@app.route("/person/delete/<int:personID>")
def delete_person_route(personID):
    if login_required():
        return redirect(url_for('login'))

    delete_person(personID)
    flash("Deleted successfully.", "success")
    return redirect(url_for('person_page'))


# ============================================================
# 3. ENTRY — Create + Read, with COMPUTED VALUE logic
#    (rename to your transaction entity, e.g. "Registration")
# ============================================================
@app.route("/entry", methods=["GET", "POST"])
def entry_page():
    if login_required():
        return redirect(url_for('login'))

    if request.method == "POST":
        personID = request.form.get("personID")
        entryMode = request.form.get("entryMode")

        # --- THE COMPUTED VALUE ---
        # Look up the person (for their discount/rate) and their group (for the base fee).
        person = get_person(personID)
        group = get_group(person["groupID"])

        base_fee = float(group["groupFee"])
        rate = float(person["personRate"])

        # EXAMPLE FORMULA — change this line to match the real spec exactly.
        # e.g. real spec said: regFPaid = evRFee - (evRFee * partDRate)
        entryAmount = base_fee - (base_fee * rate)

        entryDate = datetime.now().strftime("%Y-%m-%d")
        add_entry(personID, entryDate, entryAmount, entryMode)
        flash(f"Saved. Amount computed: {entryAmount:.2f}", "success")
        return redirect(url_for('entry_page'))

    all_entries = get_all_entries()  # already ordered latest-to-oldest in dbhelper
    all_persons = get_all_persons()  # so the add form can pick a personID
    return render_template("entry.html", entries=all_entries, persons=all_persons)


# ============================================================
# 4. MONITORING — read-only, filter dropdown + aggregate functions
# ============================================================
@app.route("/monitoring")
def monitoring():
    if login_required():
        return redirect(url_for('login'))

    groupID = request.args.get("groupID")
    rows = get_entries_joined(groupID) if groupID else get_entries_joined()

    # --- AGGREGATE FUNCTIONS ---
    count = len(rows)
    total_paid = sum(r["entryAmount"] for r in rows)

    # Total discount = (count * full_fee) - total_paid
    # Only meaningful when filtered to ONE group, since groupFee differs per group.
    total_discount = 0
    if rows:
        full_fee = float(rows[0]["groupFee"])
        total_discount = (count * full_fee) - total_paid

    all_groups = get_all_groups()  # populates the filter dropdown
    return render_template(
        "monitoring.html",
        rows=rows, groups=all_groups, selected_group=groupID,
        count=count, total_paid=total_paid, total_discount=total_discount
    )


if __name__ == "__main__":
    app.run(debug=True)
