from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    commission = db.Column(db.Float, nullable=False)
    on_demand = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('job_posts', lazy=True))

class Payment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)         # e.g. "phone", "ic", etc.
    id_value = db.Column(db.String(100), nullable=False)    # e.g. the phone number, IC number, etc.
    date_added = db.Column(db.DateTime, default=datetime.utcnow)