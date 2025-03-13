from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.city import City, Attraction
from app.models.booking import Booking, ChatSession, ChatMessage
from app.models.user import UserPreference
from app.utils.chatgpt import ChatGPTRecommender
from app import db
from datetime import datetime
import uuid

api_bp = Blueprint('api', __name__)

# Chat API routes
@api_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Process a chat message and get a response."""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400
    
    # Get or create chat session
    chat_session = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not chat_session:
        # Create new session
        session_key = str(uuid.uuid4())
        chat_session = ChatSession(user_id=current_user.id, session_key=session_key)
        db.session.add(chat_session)
        db.session.commit()
    
    # Save user message
    user_message = ChatMessage(
        session_id=chat_session.id,
        content=data['message'],
        role='user'
    )
    db.session.add(user_message)
    db.session.commit()
    
    # Process message with ChatGPT
    recommender = ChatGPTRecommender()
    
    # Get previous messages for context
    previous_messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.created_at).all()
    for msg in previous_messages:
        recommender.add_message(msg.role, msg.content)
    
    # Get response from ChatGPT
    response_text = recommender.ask_follow_up_question(data['message'])
    
    # Save assistant message
    assistant_message = ChatMessage(
        session_id=chat_session.id,
        content=response_text,
        role='assistant'
    )
    db.session.add(assistant_message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': response_text
    })

@api_bp.route('/chat/start', methods=['POST'])
@login_required
def start_chat():
    """Start a new chat session."""
    # Check if user already has an active session
    existing_session = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if existing_session:
        # Deactivate existing session
        existing_session.is_active = False
        db.session.commit()
    
    # Create new session
    session_key = str(uuid.uuid4())
    new_session = ChatSession(user_id=current_user.id, session_key=session_key)
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session_id': new_session.id,
        'session_key': session_key
    })

@api_bp.route('/chat/message', methods=['POST'])
@login_required
def send_message():
    """Send a message to the chat and get a response."""
    data = request.json
    
    if not data or 'message' not in data or 'session_id' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400
    
    # Get chat session
    session_id = data['session_id']
    chat_session = ChatSession.query.get(session_id)
    
    if not chat_session or chat_session.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Invalid session'}), 404
    
    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        content=data['message'],
        role='user'
    )
    db.session.add(user_message)
    db.session.commit()
    
    # Process message with ChatGPT
    recommender = ChatGPTRecommender()
    
    # Get previous messages for context
    previous_messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
    for msg in previous_messages:
        recommender.add_message(msg.role, msg.content)
    
    # Check if this is a preference message
    if 'preferences' in data:
        preferences = data['preferences']
        recommended_cities, response_text = recommender.get_city_recommendations(preferences)
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            content=response_text,
            role='assistant',
            contains_recommendation=True
        )
        
        # If cities were recommended, link them to the message
        if recommended_cities:
            for city in recommended_cities:
                assistant_message.recommended_city_id = city.id
                break  # Just link the first city for now
        
        db.session.add(assistant_message)
        db.session.commit()
        
        # Update user preferences
        user_prefs = UserPreference.query.filter_by(user_id=current_user.id).first()
        if user_prefs:
            if 'season' in preferences:
                user_prefs.preferred_season = preferences['season']
            if 'budget' in preferences:
                user_prefs.budget_range = preferences['budget']
            if 'interests' in preferences:
                user_prefs.interests = ','.join(preferences['interests'])
            if 'companions' in preferences:
                user_prefs.travel_companions = preferences['companions']
            if 'goals' in preferences:
                user_prefs.visit_goals = preferences['goals']
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': response_text,
            'recommended_cities': [{'id': city.id, 'name': city.name} for city in recommended_cities]
        })
    else:
        # Regular follow-up question
        response_text = recommender.ask_follow_up_question(data['message'])
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            content=response_text,
            role='assistant'
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': response_text
        })

# City API routes
@api_bp.route('/cities', methods=['GET'])
def get_cities():
    """Get all cities or filter by parameters."""
    # Get query parameters
    season = request.args.get('season')
    budget = request.args.get('budget')
    interests = request.args.get('interests')
    name = request.args.get('name')
    
    # Start with all cities
    query = City.query
    
    # Apply filters if provided
    if season:
        query = query.filter(City.best_seasons.like(f'%{season}%'))
    
    if budget:
        query = query.filter(City.budget_category == budget)
    
    if name:
        query = query.filter(City.name.ilike(f'%{name}%'))
    
    # Get cities
    cities = query.all()
    
    # Convert to JSON
    cities_data = [{
        'id': city.id,
        'name': city.name,
        'description': city.description,
        'image_url': city.image_url,
        'best_seasons': city.best_seasons,
        'budget_category': city.budget_category
    } for city in cities]
    
    return jsonify(cities_data)

@api_bp.route('/cities/<int:city_id>', methods=['GET'])
def get_city(city_id):
    """Get a specific city by ID."""
    city = City.query.get_or_404(city_id)
    
    # Get attractions for this city
    attractions = Attraction.query.filter_by(city_id=city_id).all()
    attractions_data = [{
        'id': attraction.id,
        'name': attraction.name,
        'description': attraction.description,
        'image_url': attraction.image_url,
        'category': attraction.category,
        'address': attraction.address,
        'visiting_hours': attraction.visiting_hours,
        'entrance_fee': attraction.entrance_fee
    } for attraction in attractions]
    
    # Convert to JSON
    city_data = {
        'id': city.id,
        'name': city.name,
        'description': city.description,
        'image_url': city.image_url,
        'latitude': city.latitude,
        'longitude': city.longitude,
        'best_seasons': city.best_seasons,
        'budget_category': city.budget_category,
        'attractions': attractions_data
    }
    
    return jsonify(city_data)

# Booking API routes
@api_bp.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    """Get all bookings for the current user."""
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    
    # Convert to JSON
    bookings_data = [{
        'id': booking.id,
        'city_id': booking.city_id,
        'city_name': booking.city.name,
        'start_date': booking.start_date.strftime('%Y-%m-%d'),
        'end_date': booking.end_date.strftime('%Y-%m-%d'),
        'status': booking.status,
        'total_price': booking.total_price
    } for booking in bookings]
    
    return jsonify(bookings_data)

@api_bp.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking."""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['city_id', 'start_date', 'end_date', 'num_travelers']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    try:
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Calculate number of nights
        num_nights = (end_date - start_date).days
        if num_nights <= 0:
            return jsonify({'success': False, 'error': 'End date must be after start date'}), 400
        
        # Get city information for budget calculation
        city = City.query.get(data['city_id'])
        if not city:
            return jsonify({'success': False, 'error': 'City not found'}), 404
        
        # Calculate total price based on budget category, number of nights, and number of travelers
        daily_price = 0
        if city.budget_category == 'Low':
            daily_price = 50  # $50/day for low budget
        elif city.budget_category == 'Medium':
            daily_price = 100  # $100/day for medium budget
        else:  # High budget
            daily_price = 150  # $150/day for high budget
        
        # Calculate total price
        total_price = daily_price * num_nights * int(data['num_travelers'])
        
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            city_id=data['city_id'],
            start_date=start_date,
            end_date=end_date,
            num_travelers=data['num_travelers'],
            total_price=total_price,
            notes=data.get('notes', '')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking_id': booking.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get a specific booking by ID."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Convert to JSON
    booking_data = {
        'id': booking.id,
        'city_id': booking.city_id,
        'city_name': booking.city.name,
        'start_date': booking.start_date.strftime('%Y-%m-%d'),
        'end_date': booking.end_date.strftime('%Y-%m-%d'),
        'num_travelers': booking.num_travelers,
        'status': booking.status,
        'total_price': booking.total_price,
        'payment_status': booking.payment_status,
        'notes': booking.notes,
        'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify(booking_data)

@api_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
@login_required
def update_booking(booking_id):
    """Update a specific booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    try:
        # Check if we need to recalculate the price
        recalculate_price = False
        
        # Update fields if provided
        if 'start_date' in data:
            booking.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            recalculate_price = True
        
        if 'end_date' in data:
            booking.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            recalculate_price = True
        
        if 'num_travelers' in data:
            booking.num_travelers = data['num_travelers']
            recalculate_price = True
        
        if 'status' in data:
            booking.status = data['status']
        
        if 'payment_status' in data:
            booking.payment_status = data['payment_status']
        
        if 'notes' in data:
            booking.notes = data['notes']
        
        # Recalculate total price if needed
        if recalculate_price:
            # Calculate number of nights
            num_nights = (booking.end_date - booking.start_date).days
            if num_nights <= 0:
                return jsonify({'success': False, 'error': 'End date must be after start date'}), 400
            
            # Get city information for budget calculation
            city = City.query.get(booking.city_id)
            if not city:
                return jsonify({'success': False, 'error': 'City not found'}), 404
            
            # Calculate total price based on budget category, number of nights, and number of travelers
            daily_price = 0
            if city.budget_category == 'Low':
                daily_price = 50  # $50/day for low budget
            elif city.budget_category == 'Medium':
                daily_price = 100  # $100/day for medium budget
            else:  # High budget
                daily_price = 150  # $150/day for high budget
            
            # Calculate total price
            booking.total_price = daily_price * num_nights * booking.num_travelers
        elif 'total_price' in data:
            booking.total_price = data['total_price']
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    """Delete a specific booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# User preferences API routes
@api_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get the current user's preferences."""
    preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
    
    if not preferences:
        return jsonify({})
    
    # Convert to JSON
    preferences_data = {
        'preferred_season': preferences.preferred_season,
        'budget_range': preferences.budget_range,
        'interests': preferences.interests.split(',') if preferences.interests else [],
        'travel_companions': preferences.travel_companions,
        'visit_goals': preferences.visit_goals
    }
    
    return jsonify(preferences_data)

@api_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """Update the current user's preferences."""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
    
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.session.add(preferences)
    
    try:
        # Update fields if provided
        if 'preferred_season' in data:
            preferences.preferred_season = data['preferred_season']
        
        if 'budget_range' in data:
            preferences.budget_range = data['budget_range']
        
        if 'interests' in data:
            preferences.interests = ','.join(data['interests']) if isinstance(data['interests'], list) else data['interests']
        
        if 'travel_companions' in data:
            preferences.travel_companions = data['travel_companions']
        
        if 'visit_goals' in data:
            preferences.visit_goals = data['visit_goals']
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
