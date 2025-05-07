import re, random
from flask import Flask, redirect, url_for, render_template, flash, g, session, request
from flask_mail import Mail, Message 
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, JobPost, Payment, Contact
from config import Config

app = Flask(__name__) 

app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all() 

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

    if g.user:
        app.jinja_env.globals["g_user"] = g.user
    else:
        app.jinja_env.globals["g_user"] = None  

# Guest Page

@app.route("/")
def guest():
    return render_template("guest.html")

# Register Page

@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        flash("You're already logged in!", "info")
        return redirect(url_for("profile", usr=g.user.username))
    # This checks if the user got here through submitting the form using "POST" method if not, 
    # it will run |return render_template("register.html")|
    
    if request.method == "POST":            
        email = request.form.get("email")  
        username = request.form.get("username")
        password = request.form.get("password")
        
        # This checks if the email entered is mmu domain or not
        #if not re.match(r"^[a-zA-Z0-9._%+-]+@[\w.]*mmu.edu.my$", email):
            #flash("Email must be from MMU domain!", "error")
            #return redirect(url_for("register"))
        # This checks if the email & username entered is already in the database or not
        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        
        if existing_email:
            flash("Email already taken!", "error")
            return redirect(url_for("register"))

        if existing_username:
            flash("Username already taken!", "error")
            return redirect(url_for("register"))
        # This generates a random 6 digit otp
        otp = str(random.randint(100000, 999999))
        # This stores the following information in the session to be used at otp page later
        session["otp"] = otp
        session["temp_email"] = email
        session["temp_username"] = username
        session["temp_password"] = password
        # This sends email containing otp code to the entered email 
        msg = Message("Your OTP Code", sender="hannannaimy@gmail.com", recipients=[email])
        msg.body = f"Your OTP code is {otp}. Enter this to complete registration."
        mail.send(msg)

        flash("OTP has been sent to your email!", "success")
        return redirect(url_for("otp"))

    return render_template("register.html")

# OTP Page

@app.route("/OTP", methods=["GET", "POST"])
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
            # Removes following info from session
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

# Login Page
    
@app.route("/login", methods=["GET", "POST"])
def login():
     if g.user:
        flash("You're already logged in!", "info")
        return redirect(url_for("profile", usr=g.user.username))

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

@app.route("/forgotPassword", methods=["GET", "POST"])
def forgotPassword():
    if request.method == "POST":
        email = request.form.get("email")
        # Check if the email exists in the User table
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("The email address entered does not exist.", "error")
            return redirect(url_for("forgotPassword"))
        
        # Email is found; generate a reset code (6-digit number)
        reset_code = str(random.randint(100000, 999999))
        
        # Store the reset code and email in the session for later verification
        session["resetCode"] = reset_code
        session["temp_email"] = email
        
        # Send the reset code to the user's email
        msg = Message("Your Reset Code",
                      sender="hannannaimy@gmail.com",
                      recipients=[email])
        msg.body = f"Your reset code is {reset_code}. Enter this code to reset your password."
        mail.send(msg)
        
        flash("Reset code has been sent to your email!", "success")
        return redirect(url_for("resetCode"))
    
    return render_template("forgotpassword.html")

# Reset Code Page
@app.route("/resetCode", methods=["GET", "POST"])
def resetCode():
    if request.method == "POST":
        entered_code = request.form.get("reset_code")
        
        # Compare the entered code with the one stored in the session
        if entered_code == session.get("resetCode"):
            # Optional: Remove the reset code from the session now
            session.pop("resetCode", None)
            
            flash("Reset code verified! Please reset your password.", "success")
            return redirect(url_for("newPassword"))
        else:
            flash("Invalid reset code! Try again.", "error")
            return redirect(url_for("resetCode"))
    
    return render_template("resetcode.html")

@app.route("/newPassword", methods=["GET", "POST"])
def newPassword():
    if request.method == "POST":
        new_password = request.form.get("new_password")
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Retrieve the email from session (set during forgot/reset code process)
        email = session.get("temp_email")
        if not email:
            flash("Session expired. Please start the password reset process again.", "error")
            return redirect(url_for("forgotPassword"))
        
        # Get the user record from the database
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = hashed_password
            db.session.commit()
            # Clear the temporary email from session
            session.pop("temp_email", None)
            flash("Password updated successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("User not found.", "error")
            return redirect(url_for("newPassword"))
    
    # For GET requests, simply render the new password form.
    return render_template("newpassword.html")


# Profile Page
@app.route("/profile/<usr>", methods=["GET"])
def profile(usr):
    if g.user is None:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))
    
    jobs = g.user.job_posts
    
    if g.user.username == usr:
        return render_template("ownerprofile.html", usr=g.user.username, email=g.user.email, jobs=jobs)
    else:

        other_user = User.query.filter_by(username=usr).first()
        if not other_user:
            flash("User not found!", "error")
        return render_template("profile.html", usr=other_user.username, email=other_user.email)

    
# Looking For Page

@app.route("/lookingFor", methods=["GET", "POST"])
def lookingFor():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))
    
    if request.method == 'POST':
       title = request.form.get('title')
       description = request.form.get('description')
       commission = float(request.form.get('commission'))
       on_demand = True if request.form.get('on_demand') else False  
       user_id = g.user.id  

       new_post = JobPost(
            title=title,
            description=description,
            commission=commission,
            on_demand=on_demand,
            user_id=user_id
        )
        
       db.session.add(new_post)
       db.session.commit()

       flash("Post Created Successfully!", "success")
       return redirect(url_for('lookingFor'))
    
    jobs = JobPost.query.all()
    job_count = len(g.user.job_posts) 
    return render_template("lookingfor.html", jobs=jobs, job_count=job_count)

# Offering To Page

# History Page

# Guide

# Create Job Button Disabled Message

# Job Details Page
@app.route("/postDetails")
def postDetails():
    return render_template("postdetails.html")

@app.route("/createjob_disabled")
def createJobDisabled():
    # This route only flashes a message and then redirects
    flash("You have reached the maximum limit of 3 job listings.", "error")
    return redirect(url_for("lookingFor"))

@app.route("/paymentmethods", methods=["GET", "POST"])
def paymentMethods():
    if request.method == "POST":
        payment_type = request.form.get("type")
        id_value = request.form.get("idValue")

        # Save to DB
        new_payment = Payment(type=payment_type, id_value=id_value)
        db.session.add(new_payment)
        db.session.commit()

        flash("Payment method saved successfully!", "success")
        return redirect(url_for("paymentMethods"))

    return render_template("payment.html")

# Delete Job Function

@app.route("/deletejob/<int:job_id>", methods=["POST"])
def deleteJob(job_id):
    # Ensure that a user is logged in
    if not g.user:
        flash("You must be logged in to perform that action.", "error")
        return redirect(url_for("login"))
    
    # Look up the job post by its ID
    job = JobPost.query.get(job_id)
    if job is None:
        flash("Job post not found.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    # Verify that the current user owns this job post
    if job.user_id != g.user.id:
        flash("You do not have permission to delete this job post.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    # Delete the job post and commit the changes to the database
    db.session.delete(job)
    db.session.commit()
    
    flash("Job post deleted successfully.", "success")
    return redirect(url_for("profile", usr=g.user.username))

# Logout Function
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("guest"))  

@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        phone_number = request.form.get("phone_number")
        instagram_username = request.form.get("instagram_username")
        discord_username = request.form.get("discord_username")

        # Save contact information to the database
        new_contact = Contact(
            user_id=g.user.id,
            phone_number=phone_number,
            instagram_username=instagram_username,
            discord_username=discord_username
        )
        db.session.add(new_contact)
        db.session.commit()

        flash("Contact information saved successfully!", "success")
        return redirect(url_for("contacts"))

    # Retrieve existing contact information for the logged-in user
    contact = Contact.query.filter_by(user_id=g.user.id).first()
    return render_template("contacts.html", contact=contact)










if __name__ == "__main__":
    app.run(debug=True)
