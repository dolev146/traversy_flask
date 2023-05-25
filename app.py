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
        password = sha256_crypt.encrypt(str(form.password.data))

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


if __name__ == "__main__":
    app.run(debug=True)
