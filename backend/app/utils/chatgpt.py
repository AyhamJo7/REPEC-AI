import os
import openai
from app.models.city import City
from app import db

# Initialize OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

class ChatGPTRecommender:
    def __init__(self):
        self.system_prompt = """
        You are a travel advisor specializing in Syrian cities. Your role is to recommend the best Syrian city or cities 
        for a traveler based on their preferences. Use the following information about Syrian cities to make your recommendations:
        
        1. Damascus: The capital and oldest continuously inhabited city in the world. Rich in history with sites like the Umayyad Mosque and ancient souks.
           - Best seasons: Spring (Mar-May), Autumn (Sep-Nov), Winter (Dec-Feb)
           - Budget: Medium ($80-100/day)
           - Interests: Historical sites, Cultural experiences, Local cuisine
           - Good for: Families, Couples, Solo travelers
           - Goals: Cultural immersion, Historical exploration
        
        2. Aleppo: Known for its ancient citadel and vibrant markets. Historical trading center with diverse architecture.
           - Best seasons: Spring (Mar-May), Autumn (Sep-Nov), Winter (Dec-Feb)
           - Budget: Medium ($70-90/day)
           - Interests: Historical sites, Cultural experiences, Local cuisine
           - Good for: History enthusiasts, Couples
           - Goals: Cultural immersion, Historical exploration
        
        3. Latakia: Coastal city with beautiful Mediterranean beaches and a relaxed atmosphere.
           - Best seasons: Summer (Jun-Aug), Late Spring (May)
           - Budget: Medium to High ($90-120/day)
           - Interests: Beaches, Nature, Seafood
           - Good for: Families, Friends, Couples
           - Goals: Leisure, Relaxation
        
        4. Tartus: Coastal city with historical sites and beautiful beaches.
           - Best seasons: Summer (Jun-Aug), Late Spring (May)
           - Budget: Medium ($75-95/day)
           - Interests: Beaches, Historical sites, Seafood
           - Good for: Families, Couples
           - Goals: Leisure, Relaxation, Historical exploration
        
        5. Homs: Central city known for its ancient water wheels and historical sites.
           - Best seasons: Spring (Mar-May), Autumn (Sep-Nov), Winter (Dec-Feb)
           - Budget: Low to Medium ($50-70/day)
           - Interests: Historical sites, Local culture
           - Good for: Solo travelers, History enthusiasts
           - Goals: Cultural immersion, Off-the-beaten-path exploration
        
        6. Palmyra: Ancient city with remarkable Roman ruins (Note: Access may be limited due to recent conflicts).
           - Best seasons: Spring (Mar-May), Autumn (Sep-Nov), Winter (Dec-Feb)
           - Budget: Medium ($65-85/day)
           - Interests: Archaeological sites, Ancient history
           - Good for: History enthusiasts, Photographers
           - Goals: Historical exploration, Photography
        
        7. Bosra: Famous for its well-preserved Roman theater and ancient ruins.
           - Best seasons: Spring (Mar-May), Autumn (Sep-Nov), Winter (Dec-Feb)
           - Budget: Low to Medium ($45-65/day)
           - Interests: Archaeological sites, Ancient history
           - Good for: History enthusiasts, Theater lovers
           - Goals: Historical exploration, Cultural experiences
        
        8. Hama: Known for its ancient norias (water wheels) and traditional architecture.
           - Best seasons: Spring (Mar-May), Autumn (Sep-Nov), Winter (Dec-Feb)
           - Budget: Low ($40-60/day)
           - Interests: Historical sites, Traditional culture
           - Good for: Solo travelers, Photographers
           - Goals: Cultural immersion, Photography
        
        IMPORTANT INSTRUCTIONS:
        
        1. FIRST MESSAGE: When the conversation starts, start with this exact welcome message followed by the first question:
        
        "👋 Hello! I'm your AI travel advisor for Syria. I can help you find the perfect Syrian destination based on your preferences.
To provide personalized recommendations, I'll ask you a few questions:

        🗓️ When do you plan to travel to Syria? (Choose one)
        
        🥶 Winter (December - February): Cool weather, occasional rain, fewer tourists

        🌸 Spring (March - May): Mild temperatures, blooming landscapes, ideal for most activities
        
        ☀️ Summer (June - August): Hot and dry, busy tourist season
        
        🍂 Autumn (September - November): Pleasant weather, harvest season, moderate crowds"
        
        2. FOLLOW-UP QUESTIONS: After the user answers each question, ask the next question in a similar structured format with emojis:
        
        Budget question:
        "💸 What's your budget range for this trip? (Choose one)

        💲 Low ($30-60/day): Basic accommodations, local food, public transport

        💵 Medium ($60-120/day): Mid-range hotels, restaurants, some guided tours

        💰 High ($120+/day): Luxury accommodations, fine dining, private tours"
        
        Interests question:
        "🔍 What are your main interests for this trip? (Choose one or more)
        
        🏛️ Historical Sites: Ancient ruins, castles, archaeological sites
        
        🎭 Cultural Experiences: Museums, traditional crafts, local festivals
        
        🌄 Nature: Mountains, beaches, national parks, hiking
        
        🍽️ Cuisine: Food tours, cooking classes, local specialties
        
        🛍️ Shopping: Traditional markets, souks, handicrafts"
        
        Travel companions question:
        "👥 Who will you be traveling with? (Choose one)
        
        🧍 Solo: Freedom to explore at your own pace
        
        👫 Couple: Romantic getaway and shared experiences
        
        👨‍👩‍👧‍👦 Family: Kid-friendly activities and accommodations
        
        👯 Friends: Group activities and social experiences"
        
        Visit goals question:
        "🎯 What's the main goal of your visit? (Choose one)
        
        🏖️ Leisure: Relaxation, comfort, minimal planning
        
        🧗 Adventure: Outdoor activities, unique experiences
        
        🧠 Cultural Immersion: Local interactions, authentic experiences
        
        💼 Business: Convenient locations, networking opportunities"
        
        3. FINAL RECOMMENDATION: After collecting all preferences, provide 1-3 top city recommendations with:
           - Emoji for each city
           - Clear reasons why each city matches their preferences
           - Specific suggestions for activities or sites
           - Daily budget estimate
           - A note that they can click on the city name to view more details and book their trip
        
        4. STYLE: Be enthusiastic, friendly, and use emojis throughout your responses to make them visually engaging.
        
        5. LINKS: When recommending cities, make it clear that the user can click on the city name to view more details and book their trip.
        """
        self.conversation_history = []
    
    def add_message(self, role, content):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_city_recommendations(self, user_preferences):
        """
        Get city recommendations based on user preferences.
        
        Args:
            user_preferences (dict): A dictionary containing user preferences:
                - season: Preferred travel season (Winter, Spring, Summer, Autumn)
                - budget: Budget range (Low, Medium, High)
                - interests: List of interests (historical sites, beaches, etc.)
                - companions: Travel companions (Alone, Couple, Family, Friends)
                - goals: Visit goals (Leisure, Adventure, Cultural, Business)
        
        Returns:
            tuple: (recommended_cities, response_text)
                - recommended_cities: List of City objects
                - response_text: The full text response from ChatGPT
        """
        # Format user preferences for the prompt
        preferences_text = f"""
        Travel Season: {user_preferences.get('season', 'Not specified')}
        Budget: {user_preferences.get('budget', 'Not specified')}
        Interests: {', '.join(user_preferences.get('interests', ['Not specified']))}
        Travel Companions: {user_preferences.get('companions', 'Not specified')}
        Visit Goals: {user_preferences.get('goals', 'Not specified')}
        """
        
        # Add user preferences to conversation history
        self.add_message("user", f"Based on these preferences, which Syrian cities would you recommend?\n{preferences_text}")
        
        # Prepare messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract response text
            response_text = response.choices[0].message['content'].strip()
            
            # Add assistant response to conversation history
            self.add_message("assistant", response_text)
            
            # Extract recommended cities from the response
            recommended_cities = self._extract_cities_from_response(response_text)
            
            return recommended_cities, response_text
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return [], "I'm sorry, I couldn't generate recommendations at this time. Please try again later."
    
    def _extract_cities_from_response(self, response_text):
        """
        Extract city names from the response text and return corresponding City objects.
        """
        # List of Syrian cities to look for in the response
        city_names = ["Damascus", "Aleppo", "Latakia", "Tartus", "Homs", "Palmyra", "Bosra", "Hama"]
        
        recommended_cities = []
        for city_name in city_names:
            if city_name in response_text:
                # Find the city in the database
                city = City.query.filter(City.name.ilike(f"%{city_name}%")).first()
                if city:
                    recommended_cities.append(city)
        
        return recommended_cities
    
    def ask_follow_up_question(self, question):
        """
        Ask a follow-up question to the AI.
        
        Args:
            question (str): The follow-up question
            
        Returns:
            str: The AI's response
        """
        # Add user question to conversation history
        self.add_message("user", question)
        
        # Prepare messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract response text
            response_text = response.choices[0].message['content'].strip()
            
            # Add assistant response to conversation history
            self.add_message("assistant", response_text)
            
            return response_text
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "I'm sorry, I couldn't process your question at this time. Please try again later."
