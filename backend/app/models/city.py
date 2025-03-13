from datetime import datetime
from app import db

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    
    # Geographic information
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Seasonal information
    best_seasons = db.Column(db.String(100))  # Comma-separated list of seasons
    
    # Budget information
    budget_category = db.Column(db.String(20))  # Low, Medium, High
    
    # Relationships
    attractions = db.relationship('Attraction', backref='city', lazy='dynamic')
    bookings = db.relationship('Booking', backref='city', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<City {self.name}>'

class Attraction(db.Model):
    __tablename__ = 'attractions'
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    
    # Type of attraction
    category = db.Column(db.String(50))  # Historical, Cultural, Natural, Culinary, etc.
    
    # Additional information
    address = db.Column(db.String(255))
    visiting_hours = db.Column(db.String(255))
    entrance_fee = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attraction {self.name} in {self.city.name}>'
