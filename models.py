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
    phone_number = db.Column(db.String(15), nullable=True)
    instagram_username = db.Column(db.String(50), nullable=True)
    discord_username = db.Column(db.String(50), nullable=True)
    profile_picture = db.Column(db.String(150), nullable=True, default='static/profiles/default.png')

    # Relationship to Payment methods
    payments = db.relationship('Payment', backref='user', lazy=True)

class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    commission = db.Column(db.Float, nullable=True)
    on_demand = db.Column(db.Boolean, nullable=False, default=False)
    salary_range = db.Column(db.String(50), nullable=True)
    
    # Date fields:
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_taken = db.Column(db.DateTime, nullable=True)
    date_completed = db.Column(db.DateTime, nullable=True)
    
    # Indicates if the job has been taken:
    taken = db.Column(db.Boolean, default=False)
    taken_by = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_jobpost_taken_by"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_jobpost_user"), nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[user_id], backref=db.backref('job_posts', lazy=True))
    taker = db.relationship('User', foreign_keys=[taken_by], post_update=True)
    
    # Confirmation flags:
    creator_confirmed = db.Column(db.Boolean, default=False)
    taker_confirmed = db.Column(db.Boolean, default=False)
    
    @property
    def is_complete(self):
        """Job is complete only when both the creator and the taker have confirmed."""
        return self.creator_confirmed and self.taker_confirmed

class OfferPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    commission = db.Column(db.Float, nullable=True)
    on_demand = db.Column(db.Boolean, nullable=False, default=False)
    salary_range = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # New field for offers
    
    # Indicates if the offer has been accepted:
    accepted = db.Column(db.Boolean, default=False)
    accepted_by = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_offerpost_accepted_by"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_offerpost_user"), nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[user_id], backref=db.backref('offer_posts', lazy=True))
    responder = db.relationship('User', foreign_keys=[accepted_by], post_update=True)
    
    # Added confirmation flags:
    creator_confirmed = db.Column(db.Boolean, default=False)
    responder_confirmed = db.Column(db.Boolean, default=False)
    
    @property
    def is_complete(self):
        """Offer is complete only when both the creator and the responder have confirmed."""
        return self.creator_confirmed and self.responder_confirmed

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # e.g., "Phone Number", "IC Number", etc.
    id_value = db.Column(db.String(100), nullable=False)
    is_main = db.Column(db.Boolean, default=False)  # Marks if this record is the main payment method
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    transfer_info = db.Column(db.String(200), nullable=True)  # Column for payment transfer info

    # Associate payment method with a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_payment_user"), nullable=False)

    def __repr__(self):
        return f"<Payment {self.type}: {self.id_value} for user {self.user_id}>"
