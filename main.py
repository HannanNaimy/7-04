import re, os
from flask import Flask, redirect, url_for, render_template, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = os.urandom(11)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def guest():
    return render_template("guest.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')  
        username = request.form.get('username')
        password = request.form.get('password')

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[\w.]*mmu.edu.my$', email):
            flash("Email must be from MMU domain!", "error")
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        
        if existing_email:
            flash("Email already registered!", "error")
            return redirect(url_for('register'))
        
        if existing_username:
            flash("Username already taken!", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login', email=email))

    return render_template("register.html")

    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")

            return redirect(url_for("profile", usr=username))
        else:
            flash("Invalid username or password!", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/OTP", methods=["POST"])
def otp():
    return render_template("otp.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("guest"))

@app.route("/profile/<usr>", methods=["GET", "POST"])
@app.route("/profile/<usr>", methods=["GET", "POST"])
def profile(usr):
    if "user_id" not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=usr).first()

    if not user:
        flash("User not found!", "error")
        return redirect(url_for("login"))

    if user.id == session.get("user_id"):
        return render_template("ownerprofile.html", usr=usr, email=user.email)
    else:
        return render_template("profile.html", usr=usr, email=user.email)

if __name__ == "__main__":
    app.run(debug=True)
