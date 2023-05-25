from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    session,
    logging,
)
from flask_pymongo import PyMongo
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

app.config[
    "MONGO_URI"
] = "mongodb+srv://dolev146:abc@maincluster.4asizrs.mongodb.net/users"
mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    print(f"data= {data}")

    user_name = data["username"]
    user_email = data["email"]
    print(f"user_name= {user_name}")
    print(f"user_email= {user_email}")

    user_collection = mongo.db.users
    user_collection.insert_one({"username": user_name, "email": user_email})
    # or use insert_many to insert multiple documents

    return jsonify({"status": "User added successfully"}), 201


class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords do not match"),
        ],
    )
    confirm = PasswordField("Confirm Password")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(str(form.password.data))

        user_collection = mongo.db.users
        user_collection.insert_one(
            {"name": name, "username": username, "email": email, "password": password}
        )

        flash("You are now registered and can log in", "success")

        return redirect(url_for("index"))
    return render_template("register.html", form=form)


@app.route("/showid/<string:id>/", methods=["GET"])
def showid(id):
    return render_template("showid.html", id=id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get Form Fields
        username = request.form["username"]
        password_candidate = request.form["password"]

        # Get user by username
        user_collection = mongo.db.users
        result = user_collection.find_one({"username": username})
        if result:
            print(f"result= {result}")
            # Get stored hash
            password = result["password"]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid login"
                return render_template("login.html", error=error)
            # Close connection
        else:
            error = "Username not found"
            return render_template("login.html", error=error)
    return render_template("login.html")


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please login", "danger")
            return redirect(url_for("login"))

    return wrap


@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template("dashboard.html")


# logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.secret_key = "secret123"
    app.run(debug=True)
