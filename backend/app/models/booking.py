from datetime import datetime
from app import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    
    # Booking details
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    num_travelers = db.Column(db.Integer, default=1)
    
    # Booking status
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    
    # Payment information
    total_price = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid
    
    # Additional information
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Booking {self.id} for {self.user_id} to {self.city_id}>'

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session information
    session_key = db.Column(db.String(64), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatSession {self.id} for User {self.user_id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    # Message content
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    
    # Recommendation data (if this message contains a recommendation)
    contains_recommendation = db.Column(db.Boolean, default=False)
    recommended_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id} in Session {self.session_id}>'
