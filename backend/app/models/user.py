from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth related fields
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    preferences = db.relationship('UserPreference', backref='user', uselist=False)
    
    def __init__(self, username, email, password=None, **kwargs):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    # Travel preferences
    preferred_season = db.Column(db.String(20))  # Winter, Spring, Summer, Autumn
    budget_range = db.Column(db.String(20))      # Low, Medium, High
    interests = db.Column(db.String(255))        # Comma-separated list of interests
    travel_companions = db.Column(db.String(20)) # Alone, Couple, Family, Friends
    visit_goals = db.Column(db.String(50))       # Leisure, Adventure, Cultural, Business
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference for User {self.user_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
