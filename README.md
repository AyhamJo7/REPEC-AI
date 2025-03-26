<img src="frontend/static/images/logo.png" alt="Syrian Compass Logo" width="200"/>

## Reservation Efficiency Platform Easy Convenient Artifical Intelligence
## Syrian Cities Booking & AI Recommendation Platform

A locally hosted booking website exclusively focused on Syrian cities. It allows users to search, explore, and book travel experiences across various Syrian destinations. The platform features an integrated AI-driven recommendation engine (powered by the ChatGPT API) that interacts with users via a conversational chat interface.

## Features

- **User Account and Authentication**
  - Registration and Login
  - Gmail-based authentication via OAuth
  - User Profiles

- **AI-Powered Interactive Chat**
  - Personalized travel recommendations based on preferences
  - Guided questions about travel timing, budget, interests, companions, and goals

- **Booking and Search Functionality**
  - Search interface with filters
  - Comprehensive city details
  - Seamless booking process

- **Post-Booking Engagement**
  - Booking history
  - Personalized follow-up recommendations

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/aabousika/REPEC-AI.git
   cd REPEC-AI
   ```

2. **Create and activate a virtual environment**

   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Create a .env file in the backend directory**

   Create a file named `.env` in the `backend` directory with the following content:

   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-api-key
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

   Replace the placeholder values with your actual keys.

5. **Initialize the database**

   ```bash
   cd backend
   python init_db.py
   ```

## Running the Application

1. **Start the Flask server**

   ```bash
   cd backend
   flask run 
   OR
   python run.py
   ```

2. **Access the application**

   Open your web browser and navigate to `http://127.0.0.1:5000`

## Default Login

- **Username**: admin
- **Password**: password

## Project Structure

- `backend/` - Flask backend
  - `app/` - Application code
    - `models/` - Database models
    - `routes/` - API routes and views
    - `utils/` - Utility functions
  - `instance/` - Instance-specific files (database)
  - `migrations/` - Database migrations
  - `requirements.txt` - Python dependencies
  - `run.py` - Application entry point
  - `init_db.py` - Database initialization script

- `frontend/` - Frontend assets
  - `templates/` - HTML templates
    - `auth/` - Authentication-related templates
    - `main/` - Main application templates
  - `static/` - Static files (CSS, JS, images)
    - `images/` - Image assets
      - `cities/` - City-specific images

## Environment Variables

- `FLASK_APP`: The entry point to the Flask application
- `FLASK_ENV`: The environment to run Flask in (development, production)
- `SECRET_KEY`: Secret key for session management
- `OPENAI_API_KEY`: API key for OpenAI's ChatGPT
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

## License

This project is licensed under the MIT License - see the LICENSE file for details.
