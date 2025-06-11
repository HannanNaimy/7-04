import os, re, random
from sqlalchemy import or_
from flask import Flask, redirect, url_for, render_template, flash, make_response, g, session, request
from flask_mail import Mail, Message
from flask_migrate import Migrate 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, User, JobPost, Payment, OfferPost
from config import Config
app = Flask(__name__) 
app.config.from_object(Config)

# Ensure upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

if not os.path.exists(app.config["POST_PICTURE_FOLDER"]):
    os.makedirs(app.config["POST_PICTURE_FOLDER"])

db.init_app(app)
mail = Mail(app)
migrate = Migrate(app, db)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

    app.jinja_env.globals["g_user"] = g.user if g.user else None
 
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
    if "user_id" not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=usr).first()
    if not user:
        flash("User not found!", "error")
        return redirect(url_for("login"))

    if user.id == session.get("user_id"):
        # Listed posts: jobs created by you and still available.
        listed_jobs = JobPost.query.filter_by(user_id=user.id, taken=False).all()

        # Ongoing jobs: taken but not completed (i.e. either confirmation flag is not True)
        ongoing_created_jobs = JobPost.query.filter(
            JobPost.user_id == user.id,
            JobPost.taken == True,
            or_(JobPost.creator_confirmed != True, JobPost.taker_confirmed != True)
        ).all()

        ongoing_taken_jobs = JobPost.query.filter(
            JobPost.taken == True,
            JobPost.taken_by == user.id,
            JobPost.user_id != user.id,  # Ensures you are not the creator
            or_(JobPost.creator_confirmed != True, JobPost.taker_confirmed != True)
        ).all()

        # Completed jobs: job is complete if both confirmations are True.
        completed_created_jobs = JobPost.query.filter(
            JobPost.user_id == user.id,
            JobPost.taken == True,
            JobPost.creator_confirmed == True,
            JobPost.taker_confirmed == True
        ).all()

        completed_taken_jobs = JobPost.query.filter(
            JobPost.taken == True,
            JobPost.taken_by == user.id,
            JobPost.user_id != user.id,
            JobPost.creator_confirmed == True,
            JobPost.taker_confirmed == True
        ).all()

        # Offer Posts queries
        # Offers created by user and not yet accepted
        listed_offer_posts = OfferPost.query.filter_by(user_id=user.id, accepted=False).all()

        # Offers created by user and accepted but not completed (either confirmation is not True)
        accepted_offer_posts_created = OfferPost.query.filter(
            OfferPost.user_id == user.id,
            OfferPost.accepted == True,
            or_(OfferPost.creator_confirmed != True, OfferPost.responder_confirmed != True)
        ).all()

        # Offers accepted by user (not created by user) and not completed (either confirmation is not True)
        accepted_offer_posts_taken = OfferPost.query.filter(
            OfferPost.accepted == True,
            OfferPost.accepted_by == user.id,
            OfferPost.user_id != user.id,
            or_(OfferPost.creator_confirmed != True, OfferPost.responder_confirmed != True)
        ).all()

        # Offers created by user and completed (both confirmations True)
        completed_offer_posts_created = OfferPost.query.filter(
            OfferPost.user_id == user.id,
            OfferPost.accepted == True,
            OfferPost.creator_confirmed == True,
            OfferPost.responder_confirmed == True
        ).all()

        # Offers accepted by user (not created by user) and completed (both confirmations True)
        completed_offer_posts_taken = OfferPost.query.filter(
            OfferPost.accepted == True,
            OfferPost.accepted_by == user.id,
            OfferPost.user_id != user.id,
            OfferPost.creator_confirmed == True,
            OfferPost.responder_confirmed == True
        ).all()

        return render_template("ownerprofile.html",
                       usr=user,  # pass the full user object
                       listed_jobs=listed_jobs,
                       ongoing_created_jobs=ongoing_created_jobs,
                       ongoing_taken_jobs=ongoing_taken_jobs,
                       completed_created_jobs=completed_created_jobs,
                       completed_taken_jobs=completed_taken_jobs,
                       listed_offer_posts=listed_offer_posts,
                       accepted_offer_posts_created=accepted_offer_posts_created,
                       accepted_offer_posts_taken=accepted_offer_posts_taken,
                       completed_offer_posts_created=completed_offer_posts_created,
                       completed_offer_posts_taken=completed_offer_posts_taken)

    else:
        # Pass the user instance to the template so that 'user.profile_picture' is defined.
        return render_template("profile.html", usr=user)

# Looking For Page  
@app.route("/lookingFor", methods=["GET", "POST"])
def lookingFor():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        on_demand = True if request.form.get('on_demand') else False  
        user_id = g.user.id  

        # --- Enforce post limits ---
        user_jobs = g.user.job_posts
        on_demand_count = sum(1 for job in user_jobs if job.on_demand)
        not_on_demand_count = sum(1 for job in user_jobs if not job.on_demand)
        if on_demand and on_demand_count >= 3:
            flash("You have reached the maximum limit of 3 Instant (on-demand) posts.", "error")
            return redirect(url_for("lookingFor"))
        if not on_demand and not_on_demand_count >= 7:
            flash("You have reached the maximum limit of 7 Negotiate (not on-demand) posts.", "error")
            return redirect(url_for("lookingFor"))

        # --- Handle picture upload ---
        picture_path = None
        if 'picture' in request.files:
            file = request.files['picture']
            if file and file.filename != "":
                if not allowed_file(file.filename):
                    flash("Invalid image type. Only PNG, JPG, JPEG, GIF allowed.", "error")
                    return redirect(url_for("lookingFor"))
                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                file.seek(0)
                if file_length > app.config["MAX_POST_PIC_SIZE"]:
                    flash("Image exceeds 2MB size limit.", "error")
                    return redirect(url_for("lookingFor"))
                filename = secure_filename(file.filename)
                picture_path = os.path.join(app.config["POST_PICTURE_FOLDER"], filename)
                file.save(picture_path)
                picture_path = picture_path.replace("\\", "/")  # For Windows path

        if on_demand:
            commission_input = request.form.get('commission')
            try:
                commission = float(commission_input)
            except ValueError:
                flash("Invalid commission cost. Please enter a numeric value.", "error")
                return redirect(url_for("lookingFor"))
            salary_range_value = None
        else:
            min_salary = request.form.get('min_salary')
            max_salary = request.form.get('max_salary')
            if not min_salary or not max_salary:
                flash("Please enter both a minimum and maximum salary.", "error")
                return redirect(url_for("lookingFor"))
            commission = None
            salary_range_value = f"{min_salary}-{max_salary}"

        new_post = JobPost(
            title=title,
            description=description,
            commission=commission,
            on_demand=on_demand,
            salary_range=salary_range_value,
            user_id=user_id,
            picture=picture_path  # assumes JobPost has a 'picture' field
        )
        
        db.session.add(new_post)
        db.session.commit()

        flash("Post Created Successfully!", "success")
        return redirect(url_for('lookingFor'))
    
    jobs = JobPost.query.filter_by(taken=False).all()
    # Count user's own posts for modal button logic
    user_jobs = g.user.job_posts
    on_demand_count = sum(1 for job in user_jobs if job.on_demand)
    not_on_demand_count = sum(1 for job in user_jobs if not job.on_demand)
    return render_template("lookingfor.html", jobs=jobs, job_count=len(user_jobs),
                           on_demand_jobs=[job for job in jobs if job.on_demand],
                           listing_jobs=[job for job in jobs if not job.on_demand],
                           on_demand_count=on_demand_count,
                           not_on_demand_count=not_on_demand_count)

@app.route("/offeringTo", methods=["GET", "POST"])
def offeringTo():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        on_demand = True if request.form.get('on_demand') else False
        user_id = g.user.id  

        # --- Enforce post limits ---
        user_offers = g.user.offer_posts
        on_demand_count = sum(1 for offer in user_offers if offer.on_demand)
        not_on_demand_count = sum(1 for offer in user_offers if not offer.on_demand)
        if on_demand and on_demand_count >= 3:
            flash("You have reached the maximum limit of 3 Instant (on-demand) offers.", "error")
            return redirect(url_for("offeringTo"))
        if not on_demand and not_on_demand_count >= 7:
            flash("You have reached the maximum limit of 7 Negotiate (not on-demand) offers.", "error")
            return redirect(url_for("offeringTo"))

        # --- Handle picture upload ---
        picture_path = None
        if 'picture' in request.files:
            file = request.files['picture']
            if file and file.filename != "":
                if not allowed_file(file.filename):
                    flash("Invalid image type. Only PNG, JPG, JPEG, GIF allowed.", "error")
                    return redirect(url_for("offeringTo"))
                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                file.seek(0)
                if file_length > app.config["MAX_POST_PIC_SIZE"]:
                    flash("Image exceeds 2MB size limit.", "error")
                    return redirect(url_for("offeringTo"))
                filename = secure_filename(file.filename)
                picture_path = os.path.join(app.config["POST_PICTURE_FOLDER"], filename)
                file.save(picture_path)
                picture_path = picture_path.replace("\\", "/")  # For Windows path

        if on_demand:
            commission_input = request.form.get('commission')
            try:
                commission = float(commission_input)
            except ValueError:
                flash("Invalid commission cost. Please enter a numeric value.", "error")
                return redirect(url_for("offeringTo"))
            salary_range_value = None
        else:
            min_salary = request.form.get('min_salary')
            max_salary = request.form.get('max_salary')
            if not min_salary or not max_salary:
                flash("Please enter both a minimum and maximum salary.", "error")
                return redirect(url_for("offeringTo"))
            commission = None
            salary_range_value = f"{min_salary}-{max_salary}"

        new_offer = OfferPost(
            title=title,
            description=description,
            commission=commission,
            on_demand=on_demand,
            salary_range=salary_range_value,
            user_id=user_id,
            picture=picture_path  # assumes OfferPost has a 'picture' field
        )
        
        db.session.add(new_offer)
        db.session.commit()

        flash("Offer Created Successfully!", "success")
        return redirect(url_for('offeringTo'))
    
    offers = OfferPost.query.filter_by(accepted=False).all()
    user_offers = g.user.offer_posts
    on_demand_count = sum(1 for offer in user_offers if offer.on_demand)
    not_on_demand_count = sum(1 for offer in user_offers if not offer.on_demand)
    return render_template("offeringto.html", offers=offers, offer_count=len(user_offers),
                           on_demand_offers=[offer for offer in offers if offer.on_demand],
                           listing_offers=[offer for offer in offers if not offer.on_demand],
                           on_demand_count=on_demand_count,
                           not_on_demand_count=not_on_demand_count)
 

# Job Status Page   
@app.route("/jobStatus/<int:job_id>", methods=["GET", "POST"])
def jobStatus(job_id):
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))
    
    job = JobPost.query.get(job_id)
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    # Only allow creator or taker.
    if g.user.id != job.user_id and g.user.id != job.taken_by:
        flash("You are not authorized to update the job status.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    if request.method == "POST":
        # Do not allow changes if both users have already confirmed
        if job.creator_confirmed and job.taker_confirmed:
            flash("Job is already marked as complete. Confirmation cannot be undone.", "error")
            return redirect(url_for("profile", usr=g.user.username))

        # Allow only unconfirmed users to confirm
        if g.user.id == job.user_id and not job.creator_confirmed:
            job.creator_confirmed = True
        elif g.user.id == job.taken_by and not job.taker_confirmed:
            job.taker_confirmed = True

        # If both confirmations are now true, update the completion date.
        if job.creator_confirmed and job.taker_confirmed:
            job.date_completed = datetime.utcnow()

        db.session.commit()
        
       # If both confirmed, redirect immediately.
        if job.creator_confirmed and job.taker_confirmed:
            flash("Job marked as complete!", "success")
            return redirect(url_for("profile", usr=g.user.username))
        else:
            total = int(job.creator_confirmed or 0) + int(job.taker_confirmed or 0)
            flash(f"Job confirmation updated: {total}/2", "info")
            return redirect(url_for("jobStatus", job_id=job_id))
    
    # For GET requests, if complete, redirect immediately.
    if job.creator_confirmed and job.taker_confirmed:
        return redirect(url_for("profile", usr=g.user.username))
    
    # Otherwise, render the page.
    response = make_response(render_template("jobstatus.html", job=job))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Offer Status Page
@app.route("/offerStatus/<int:offer_id>", methods=["GET", "POST"])
def offerStatus(offer_id):
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    offer = OfferPost.query.get(offer_id)
    if not offer:
        flash("Offer not found.", "error")
        return redirect(url_for("profile", usr=g.user.username))

    # Only allow creator or responder.
    if g.user.id != offer.user_id and g.user.id != offer.accepted_by:
        flash("You are not authorized to update the offer status.", "error")
        return redirect(url_for("profile", usr=g.user.username))

    if request.method == "POST":
        # Do not allow changes if both users have already confirmed
        if offer.creator_confirmed and offer.responder_confirmed:
            flash("Offer is already marked as complete. Confirmation cannot be undone.", "error")
            return redirect(url_for("profile", usr=g.user.username))

        # Allow only unconfirmed users to confirm
        if g.user.id == offer.user_id and not offer.creator_confirmed:
            offer.creator_confirmed = True
        elif g.user.id == offer.accepted_by and not offer.responder_confirmed:
            offer.responder_confirmed = True

        # If both confirmations are now true, update the completion date.
        if offer.creator_confirmed and offer.responder_confirmed:
            offer.date_completed = datetime.utcnow()

        db.session.commit()

        # If both confirmed, redirect immediately.
        if offer.creator_confirmed and offer.responder_confirmed:
            flash("Offer marked as complete!", "success")
            return redirect(url_for("profile", usr=g.user.username))
        else:
            total = int(offer.creator_confirmed or 0) + int(offer.responder_confirmed or 0)
            flash(f"Offer confirmation updated: {total}/2", "info")
            return redirect(url_for("offerStatus", offer_id=offer_id))

    # For GET requests, if complete, redirect immediately.
    if offer.creator_confirmed and offer.responder_confirmed:
        return redirect(url_for("profile", usr=g.user.username))

    # Otherwise, render the page.
    response = make_response(render_template("offerstatus.html", offer=offer))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Job Details Page
@app.route("/postDetails/<int:job_id>")
def post_details(job_id):
    job = JobPost.query.get_or_404(job_id)
    return render_template("postdetails.html", job=job)

@app.route("/offerDetails/<int:offer_id>")
def offer_details(offer_id):
    offer = OfferPost.query.get_or_404(offer_id)
    return render_template("offerdetails.html", offer=offer)

@app.route("/createjob_disabled")
def createJobDisabled():
    # This route only flashes a message and then redirects
    flash("You have reached the maximum limit of 3 job listings.", "error")
    return redirect(url_for("lookingFor"))

@app.route('/editpaymentmethods', methods=['GET', 'POST'])
def edit_payment_methods():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    if request.method == 'POST':
        # Get user inputs for all payment types.
        phone = request.form.get('phone', '').strip()
        ic = request.form.get('ic', '').strip()
        account = request.form.get('account', '').strip()
        business = request.form.get('business', '').strip()

        # Validate that at least one field is filled.
        if not any([phone, ic, account, business]):
            flash("Please enter at least one payment method.", "danger")
            return redirect("/editpaymentmethods")

        messages = []  # Collect status messages for each type.
        # Map each payment type to its corresponding submitted value.
        data = {
            "Phone Number": phone,
            "IC Number": ic,
            "Account Number": account,
            "Business Registration Number": business
        }

        for ptype, value in data.items():
            if value:  # Process this field if it is not empty.
                # Query the Payment table for a record of this type for the current user.
                existing = Payment.query.filter_by(type=ptype, user_id=g.user.id).first()
                if existing:
                    if existing.id_value == value:
                        messages.append(f"{ptype} is already set to that value; no change made.")
                    else:
                        # Update the record with the new value.
                        existing.id_value = value
                        messages.append(f"{ptype} updated successfully!")
                else:
                    # Create a new payment method record linked with the current user.
                    new_payment = Payment(type=ptype, id_value=value, user_id=g.user.id)
                    db.session.add(new_payment)
                    messages.append(f"{ptype} added successfully!")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while saving your payment method(s).", "danger")
            return redirect("/editpaymentmethods")

        flash(" ".join(messages), "success")
        return redirect("/editpaymentmethods")

    # For a GET request, retrieve only the payment methods for the logged-in user.
    saved_payments = Payment.query.filter_by(user_id=g.user.id).order_by(Payment.date_added.desc()).all()
    return render_template("payment.html", saved_payments=saved_payments)

@app.route("/history")
def historyPage():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    events = []

    # Gather job event data (existing implementation)
    created_jobs = JobPost.query.filter_by(user_id=g.user.id).all()
    for job in created_jobs:
        events.append({
            "date": job.date_created,
            "text": f"You created the job '{job.title}'.",  # Removed the duplicate date
            "payment_transfer": "-"  # No payment transfer for created jobs
        })

    taken_jobs = JobPost.query.filter_by(taken_by=g.user.id).all()
    for job in taken_jobs:
        if job.date_taken:
            events.append({
                "date": job.date_taken,
                "text": f"You took the job '{job.title}'.",  # Removed duplicate date information
                "payment_transfer": "-"  # No payment transfer for taken jobs
            })

    completed_jobs = JobPost.query.filter(
        JobPost.creator_confirmed == True,
        JobPost.taker_confirmed == True,
        ((JobPost.user_id == g.user.id) | (JobPost.taken_by == g.user.id))
    ).all()
    for job in completed_jobs:
        if job.date_completed:
            events.append({
                "date": job.date_completed,
                "text": f"Job '{job.title}' was completed.",  # Removed duplicate date information
                "payment_transfer": f"Transferred from Escrow to {job.taker.username}: Rm{job.commission}" if job.commission else "-"
            })

    payments = Payment.query.filter_by(user_id=g.user.id).all()
    for payment in payments:
        if payment.transfer_info:
            events.append({
                "date": payment.date_created,
                "text": f"Payment method '{payment.method_name}' processed.",
                "payment_transfer": payment.transfer_info
            })

    # Apply date filter
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        events = [e for e in events if e['date'] >= start_date]
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        events = [e for e in events if e['date'] <= end_date]

    # Sort events by date
    sort_order = request.args.get("sort", "desc")
    if sort_order == "asc":
        events.sort(key=lambda e: e["date"])
    else:
        events.sort(key=lambda e: e["date"], reverse=True)

    return render_template("history.html", events=events, sort_order=sort_order)

#Set Main Payment

@app.route('/setmain/<int:payment_id>', methods=['POST'])
def set_main(payment_id):
    payment_to_set = Payment.query.get(payment_id)
    if not payment_to_set:
        flash("Payment method not found.", "danger")
        return redirect("/editpaymentmethods")
    
    # For this example, only one saved payment method will be set as main overall.
    # Reset all methods' is_main flag.
    for p in Payment.query.all():
        p.is_main = False
    payment_to_set.is_main = True

    try:
        db.session.commit()
        flash(f"{payment_to_set.type} set as main successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while setting the payment method as main.", "danger")
    return redirect("/editpaymentmethods")


# Take Job Function
@app.route("/take/<int:job_id>", methods=["POST"])
def take_job(job_id):
    if not g.user:
        flash("You must be logged in to take a job.", "error")
        return redirect(url_for("login"))
    
    job = JobPost.query.get_or_404(job_id)
    
    # Prevent the posting user from taking the job.
    if job.creator.id == g.user.id:
        flash("You cannot take your own job.", "error")
        return redirect(url_for("post_details", job_id=job_id))
    
    # Check if the job is already taken:
    if job.taken:
        flash("This job has already been taken.", "error")
        return redirect(url_for("lookingFor"))
    
    # Mark the job as taken.
    job.taken = True
    job.taken_by = g.user.id
    job.date_taken = datetime.utcnow()  # Update the date_taken field.
    
    db.session.commit()
    
    flash("Job taken successfully. The listing has been removed.", "success")
    return redirect(url_for("lookingFor"))

@app.route("/take_offer/<int:offer_id>", methods=["POST"])
def take_offer(offer_id):
    if not g.user:
        flash("You must be logged in to take an offer.", "error")
        return redirect(url_for("login"))
    
    offer = OfferPost.query.get_or_404(offer_id)
    
    # Prevent the posting user from taking the offer.
    if offer.creator.id == g.user.id:
        flash("You cannot take your own offer.", "error")
        return redirect(url_for("offer_details", offer_id=offer_id))
    
    # Check if the offer is already taken:
    if offer.accepted:
        flash("This offer has already been taken.", "error")
        return redirect(url_for("offeringTo"))
    
    # Mark the offer as accepted.
    offer.accepted = True
    offer.accepted_by = g.user.id
    db.session.commit()
    
    flash("Offer accepted! The listing has been removed.", "success")
    return redirect(url_for("offeringTo"))

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
    if job.creator.id != g.user.id:
        flash("You do not have permission to delete this job post.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    # Delete the job post and commit the changes to the database
    db.session.delete(job)
    db.session.commit()
    
    flash("Job post deleted successfully.", "success")
    return redirect(url_for("profile", usr=g.user.username))

# Delete Offer Function
@app.route("/deleteoffer/<int:offer_id>", methods=["POST"])
def deleteOffer(offer_id):
    # Ensure that a user is logged in
    if not g.user:
        flash("You must be logged in to perform that action.", "error")
        return redirect(url_for("login"))
    
    # Look up the offer post by its ID
    offer = OfferPost.query.get(offer_id)
    if offer is None:
        flash("Offer post not found.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    # Verify that the current user owns this offer post
    if offer.creator.id != g.user.id:
        flash("You do not have permission to delete this offer post.", "error")
        return redirect(url_for("profile", usr=g.user.username))
    
    # Delete the offer post and commit the changes to the database
    db.session.delete(offer)
    db.session.commit()
    
    flash("Offer post deleted successfully.", "success")
    return redirect(url_for("profile", usr=g.user.username))

# User Search Function
@app.route("/search", methods=["GET"])
def search():
    # Retrieve the username from the query parameter 'q'
    username = request.args.get("q", "").strip()
    
    if not username:
        flash("Please enter a username to search.", "error")
        # Change the destination as you see fit; here, it goes back to the current user's profile.
        return redirect(url_for("profile", usr=g.user.username))
    
    # Redirect to the profile page for the searched username.
    return redirect(url_for("profile", usr=username))


# Profile Picture Upload Function
@app.route("/profilePic", methods=["POST"])
def profilePic():
    if not g.user:
        flash("You must be logged in to update your profile picture.", "error")
        return redirect(url_for("login"))

    if "profile_picture" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("editProfile"))

    file = request.files["profile_picture"]

    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("editProfile"))

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload a PNG, JPG, JPEG, or GIF.", "error")
        return redirect(url_for("editProfile"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Update user profile picture in the database
    g.user.profile_picture = filepath
    db.session.commit()

    flash("Profile picture updated successfully!", "success")
    return redirect(url_for("editProfile"))

# Logout Function
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("guest"))  

@app.route("/editProfile", methods=["GET", "POST"])
def editProfile():
    if not g.user:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        # Retrieve new contact details from the form
        phone_number = request.form.get("phone_number")
        instagram_username = request.form.get("instagram_username")
        discord_username = request.form.get("discord_username")

        # Update the user table by setting new values on g.user
        g.user.phone_number = phone_number
        g.user.instagram_username = instagram_username
        g.user.discord_username = discord_username

        # Commit the updates to the database
        db.session.commit()
        flash("Contact information updated successfully!", "success")
        return redirect(url_for("editProfile"))
    
    return render_template(
        "editprofile.html",
        usr=g.user.username,
        email=g.user.email,
        phone_number=g.user.phone_number,
        instagram_username=g.user.instagram_username,
        discord_username=g.user.discord_username
    )

@app.route("/changeUsername", methods=["GET", "POST"])
def changeUsername():
    if not g.user:
        flash("You must be logged in to change your username.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_username = request.form.get("username")
        current_password = request.form.get("password")

        # Verify the current password.
        if not check_password_hash(g.user.password, current_password):
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for("changeUsername"))
        
        if len(new_username) < 4 or len(new_username) > 12:
            flash("Username must be between 4 and 12 characters.", "error")
            return redirect(url_for("changeUsername"))

        # Ensure the new username is unique.
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != g.user.id:
            flash("Username already in use. Please choose a different username.", "error")
            return redirect(url_for("changeUsername"))

        # Update the username.
        g.user.username = new_username
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your username. Please try again.", "error")
            return redirect(url_for("changeUsername"))

        flash("Username updated successfully!", "success")
        return redirect(url_for("editProfile"))

    # For GET requests, render the edit profile page with existing details.
    return render_template(
        "editprofile.html",
        phone_number=g.user.phone_number,
        instagram_username=g.user.instagram_username,
        discord_username=g.user.discord_username
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
