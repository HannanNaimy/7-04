import re, random
from flask import Flask, redirect, url_for, render_template, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__) 
mail = Mail(app)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def guest():
    return render_template("guest.html")

#Register Page

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")  
        username = request.form.get("username")
        password = request.form.get("password")

        if not re.match(r"^[a-zA-Z0-9._%+-]+@[\w.]*mmu.edu.my$", email):
            flash("Email must be from MMU domain!", "error")
            return redirect(url_for("register"))
        
        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        
        if existing_email:
            flash("Email already taken!", "error")
            return redirect(url_for("register"))

        if existing_username:
            flash("Username already taken!", "error")
            return redirect(url_for("register"))

        # Adam's OTP start
        otp = str(random.randint(100000, 999999))

        session["otp"] = otp
        session["temp_email"] = email
        session["temp_username"] = username
        session["temp_password"] = password

        msg = Message("Your OTP Code", sender="ebtaskwebapp@outlook.com", recipients=[email])
        msg.body = f"Your OTP code is {otp}. Enter this to complete registration."
        mail.send(msg)

        flash("OTP has been sent to your email!", "success")
        return redirect(url_for("otp"))

    return render_template("register.html")

@app.route("/OTP", methods=["POST"])
def otp():
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        # Check if entered OTP matches stored OTP
        if entered_otp == session.get("otp"):
            # Hash the password and create user
            hashed_password = generate_password_hash(session["temp_password"])
            new_user = User(email=session["temp_email"], username=session["temp_username"], password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()

            # Clear session after successful registration
            session.pop("otp")
            session.pop("temp_email")
            session.pop("temp_username")
            session.pop("temp_password")

            flash("Registration successful!", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid OTP! Try again.", "error")
            return redirect(url_for("otp"))

    return render_template("otp.html")
        
        # Adam's OTP end
    
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

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("guest"))

@app.route("/profile/<usr>", methods=["GET", "POST"])
def profile(usr):
    if "user_id" not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))
    
    user = User.query.filter_by(username=usr).first()
    if user:
        return render_template("profile.html", usr=usr, email=user.email)
    else:
        flash("User not found!", "error")
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
