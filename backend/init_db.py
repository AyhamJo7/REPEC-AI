import os
import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User, UserPreference
from app.models.city import City, Attraction
from app.models.booking import Booking

def init_db():
    """Initialize the database with sample data."""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first() is not None:
            print("Database already contains data. Skipping initialization.")
            return
        
        print("Initializing database with sample data...")
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password="password",
            first_name="Admin",
            last_name="User"
        )
        db.session.add(admin)
        
        # Create user preferences for admin
        admin_prefs = UserPreference(
            user=admin,
            preferred_season="Summer",
            budget_range="Medium $$",
            interests="Historical sites,Cultural experiences,Local cuisine",
            travel_companions="Family",
            visit_goals="Cultural immersion"
        )
        db.session.add(admin_prefs)
        
        # Create sample cities
        damascus = City(
            name="Damascus",
            description="Damascus is the capital and oldest continuously inhabited city in the world. Rich in history with sites like the Umayyad Mosque and ancient souks.",
            image_url="/static/images/cities/Damascus.jpg",
            latitude=33.5138,
            longitude=36.2765,
            best_seasons="Spring,Autumn,Winter",
            budget_category="Medium $$"
        )
        db.session.add(damascus)
        
        aleppo = City(
            name="Aleppo",
            description="Aleppo is known for its ancient citadel and vibrant markets. It was a historical trading center with diverse architecture.",
            image_url="/static/images/cities/Aleppo.jpg",
            latitude=36.2021,
            longitude=37.1343,
            best_seasons="Spring,Autumn,Winter",
            budget_category="Medium $$"
        )
        db.session.add(aleppo)
        
        latakia = City(
            name="Latakia",
            description="Latakia is a coastal city with beautiful Mediterranean beaches and a relaxed atmosphere.",
            image_url="/static/images/cities/Lattakia.jpg",
            latitude=35.5317,
            longitude=35.7914,
            best_seasons="Summer,Late Spring",
            budget_category="Medium to High $$-$$$"
        )
        db.session.add(latakia)
        
        tartus = City(
            name="Tartus",
            description="Tartus is a coastal city with historical sites and beautiful beaches.",
            image_url="/static/images/cities/Tartus.jpg",
            latitude=34.8892,
            longitude=35.8878,
            best_seasons="Summer,Late Spring",
            budget_category="Medium $$"
        )
        db.session.add(tartus)
        
        homs = City(
            name="Homs",
            description="Homs is a central city known for its ancient water wheels and historical sites.",
            image_url="/static/images/cities/Homs.jpg",
            latitude=34.7324,
            longitude=36.7137,
            best_seasons="Spring,Autumn,Winter",
            budget_category="Low to Medium $-$$"
        )
        db.session.add(homs)
        
        palmyra = City(
            name="Palmyra",
            description="Palmyra is an ancient city with remarkable Roman ruins (Note: Access may be limited due to recent conflicts).",
            image_url="/static/images/cities/Palmyra.jpg",
            latitude=34.5682,
            longitude=38.2841,
            best_seasons="Spring,Autumn,Winter",
            budget_category="Medium $$"
        )
        db.session.add(palmyra)
        
        bosra = City(
            name="Bosra",
            description="Bosra is famous for its well-preserved Roman theater and ancient ruins.",
            image_url="/static/images/cities/Bosra.jpg",
            latitude=32.5168,
            longitude=36.4817,
            best_seasons="Spring,Autumn,Winter",
            budget_category="Low to Medium $-$$"
        )
        db.session.add(bosra)
        
        hama = City(
            name="Hama",
            description="Hama is known for its ancient norias (water wheels) and traditional architecture.",
            image_url="/static/images/cities/Hama.jpg",
            latitude=35.1318,
            longitude=36.7518,
            best_seasons="Spring,Autumn,Winter",
            budget_category="Low $"
        )
        db.session.add(hama)
        
        # Commit cities to get IDs
        db.session.commit()
        
        # Create attractions for Damascus
        umayyad_mosque = Attraction(
            city_id=damascus.id,
            name="Umayyad Mosque",
            description="One of the largest and oldest mosques in the world, known for its beautiful architecture and historical significance.",
            image_url="/static/images/cities/Umayyad Mosque.jpg",
            category="Historical",
            address="Al-Thawra Street, Damascus, Syria",
            visiting_hours="8:00 AM - 6:00 PM",
            entrance_fee="Free for Muslims, Small fee for non-Muslims"
        )
        db.session.add(umayyad_mosque)
        
        souq_al_hamidiyah = Attraction(
            city_id=damascus.id,
            name="Souq Al-Hamidiyah",
            description="The largest and most central souk in Damascus, covered with a metal roof dating back to Ottoman times.",
            image_url="/static/images/cities/Souq Al-Hamidiyah.jpg",
            category="Cultural",
            address="Old City, Damascus, Syria",
            visiting_hours="9:00 AM - 8:00 PM",
            entrance_fee="Free"
        )
        db.session.add(souq_al_hamidiyah)
        
        # Create attractions for Aleppo
        aleppo_citadel = Attraction(
            city_id=aleppo.id,
            name="Aleppo Citadel",
            description="A large medieval fortified palace that is one of the oldest and largest castles in the world.",
            image_url="/static/images/cities/Aleppo Citadel.jpg",
            category="Historical",
            address="Old City, Aleppo, Syria",
            visiting_hours="9:00 AM - 5:00 PM",
            entrance_fee="Small fee"
        )
        db.session.add(aleppo_citadel)
        
        # Create attractions for Latakia
        latakia_beach = Attraction(
            city_id=latakia.id,
            name="Latakia Beach",
            description="Beautiful Mediterranean beaches with clear blue water and sandy shores.",
            image_url="/static/images/cities/Latakia Beach.jpg",
            category="Natural",
            address="Corniche, Latakia, Syria",
            visiting_hours="24/7",
            entrance_fee="Free"
        )
        db.session.add(latakia_beach)
        
        # Create sample bookings
        booking1 = Booking(
            user_id=admin.id,
            city_id=damascus.id,
            start_date=(datetime.now() + timedelta(days=30)).date(),
            end_date=(datetime.now() + timedelta(days=35)).date(),
            num_travelers=2,
            status="confirmed",
            total_price=500.0,
            payment_status="paid",
            notes="Looking forward to visiting the Umayyad Mosque"
        )
        db.session.add(booking1)
        
        booking2 = Booking(
            user_id=admin.id,
            city_id=latakia.id,
            start_date=(datetime.now() + timedelta(days=60)).date(),
            end_date=(datetime.now() + timedelta(days=67)).date(),
            num_travelers=4,
            status="pending",
            total_price=800.0,
            payment_status="unpaid",
            notes="Summer beach vacation with family"
        )
        db.session.add(booking2)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
