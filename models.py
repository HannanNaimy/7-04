from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __table_args__ = (
        db.UniqueConstraint('email', name='uq_user_email'),
        db.UniqueConstraint('username', name='uq_user_username'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(12), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    commission = db.Column(db.Float, nullable=True)
    on_demand = db.Column(db.Boolean, nullable=False, default=False)
    salary_range = db.Column(db.String(50), nullable=True)
    
    # Indicates if the job has been taken:
    taken = db.Column(db.Boolean, default=False)
    taken_by = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', name="fk_jobpost_taken_by"),
        nullable=True
    )
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', name="fk_jobpost_user"), 
        nullable=False
    )
    
    # Relationship for the job creator (poster)
    creator = db.relationship(
        'User', 
        foreign_keys=[user_id],
        backref=db.backref('job_posts', lazy=True)
    )
    # Relationship for the job taker
    taker = db.relationship(
        'User',
        foreign_keys=[taken_by],
        post_update=True
    )

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)         # e.g. "phone", "ic", etc.
    id_value = db.Column(db.String(100), nullable=False)      # e.g. the phone number, IC number, etc.
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    instagram_username = db.Column(db.String(50), nullable=True)
    discord_username = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', backref=db.backref('contacts', lazy=True))