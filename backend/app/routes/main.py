from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.city import City, Attraction
from app.models.booking import Booking, ChatSession, ChatMessage
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_now():
    """Add current datetime to all templates."""
    return {'now': datetime.now()}

@main_bp.route('/')
def index():
    """Home page route."""
    # Get featured cities
    featured_cities = City.query.limit(4).all()
    return render_template('main/index.html', title='Home', featured_cities=featured_cities)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route."""
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    
    # Get user's chat sessions
    chat_sessions = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).order_by(ChatSession.updated_at.desc()).all()
    
    # Get featured cities for the dashboard
    cities = City.query.limit(3).all()
    
    return render_template('main/dashboard.html', title='Dashboard', bookings=bookings, chat_sessions=chat_sessions, cities=cities)

@main_bp.route('/cities')
def cities():
    """List all cities route."""
    # Get all cities
    all_cities = City.query.all()
    return render_template('main/cities.html', title='Explore Syrian Cities', cities=all_cities)

@main_bp.route('/cities/<int:city_id>')
def city_detail(city_id):
    """City detail route."""
    # Get city by ID
    city = City.query.get_or_404(city_id)
    
    # Get city attractions
    attractions = Attraction.query.filter_by(city_id=city_id).all()
    
    return render_template('main/city_detail.html', title=city.name, city=city, attractions=attractions)

@main_bp.route('/chat')
@login_required
def chat():
    """AI chat interface route."""
    # Deactivate any existing chat sessions
    existing_sessions = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).all()
    for session in existing_sessions:
        session.is_active = False
    db.session.commit()
    
    # Create a new chat session
    import uuid
    session_key = str(uuid.uuid4())
    chat_session = ChatSession(user_id=current_user.id, session_key=session_key)
    db.session.add(chat_session)
    db.session.commit()
    
    # No messages for the new session
    messages = []
    
    return render_template('main/chat.html', title='Travel Advisor', chat_session=chat_session, messages=messages)

@main_bp.route('/bookings')
@login_required
def bookings():
    """User bookings route."""
    # Get user's bookings
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_date).all()
    
    return render_template('main/bookings.html', title='My Bookings', bookings=user_bookings)

@main_bp.route('/bookings/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    """Booking detail route."""
    # Get booking by ID
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('You do not have permission to view this booking.', 'danger')
        return redirect(url_for('main.bookings'))
    
    return render_template('main/booking_detail.html', title='Booking Details', booking=booking)

@main_bp.route('/about')
def about():
    """About page route."""
    return render_template('main/about.html', title='About Syrian Compass')

@main_bp.route('/contact')
def contact():
    """Contact page route."""
    return render_template('main/contact.html', title='Contact Us')
