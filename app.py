import json
import sqlite3
import spotipy
import random
import os
import resend
import string

from flask import Flask, g, flash, redirect, render_template, request, session, url_for, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from openai import OpenAI
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
# I used chatgpt to help me with integrating AI implementation

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Configure application
app = Flask(__name__, template_folder='templates')

# Secret key for signing the session
app.secret_key = "the_wanderlist_anonymous"  

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('wanderlist.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Prevent caching
    response.headers["Expires"] = 0  # Make the content expire immediately
    response.headers["Pragma"] = "no-cache"  # Another directive to prevent caching
    return response

# Logs the user in
@app.route("/", methods=["GET", "POST"])
def login():
    # Check if the user is already logged in via session
    if "user_id" not in session:
        # Check if there is an email cookie
        email_cookie = request.cookies.get("email")
        if email_cookie:
            db = get_db()
            user = db.execute("SELECT * FROM users WHERE email=?", (email_cookie,)).fetchone()
            if user:
                # If the user is found, log them in and redirect to homepage
                session["user_id"] = user["id"]
                return redirect("/")
    
    if request.method == "POST":
        # Handle login attempt (get form data, validate user, etc.)
        email = request.form.get("email")
        password = request.form.get("password")
        remember_me = 'remember_me' in request.form

        # Query the database for the user
        db = get_db()  # Get the database connection inside the request context
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()    

        # Check if user exists and password is correct
        if user and check_password_hash(user['password_hash'], password):
            session["user_id"] = user["id"]
            response = redirect("/")

            if remember_me:
                response.set_cookie("email", email, max_age=timedelta(days=30), httponly=True, samesite='Lax') 

            return response           

        else:
            flash('Invalid email or password')
        
        return render_template("login.html")

    if request.method == "GET":
        if "user_id" not in session:
            return render_template("login.html")
        else:
            return render_template("homepage.html")
    

# User can sign up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Handle sign up attempt
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        # Update database
        db = get_db()
        
        # Check if user already exists
        existing_user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if existing_user:
            flash('Email already registered')
            return render_template("signup.html")

        # Insert new user
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hashed_password))
        db.commit()

        # Fetch the newly created user
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

        # Log the user in by setting the session
        session["user_id"] = user["id"]

        # Redirect to homepage after successful sign up
        return redirect("/")

    return render_template("signup.html")

# Question route (renders questions to ask the user)
@app.route("/questions", methods = ["GET", "POST"])
def questions():
    if "user_id" not in session:
        return redirect("/")
    if request.method == "POST":
        location = request.form.get("where-text")
        mood = request.form.get("mood")
        activity = request.form.get("activity")
        budget = request.form.get("budget")

        if not location or not mood or not activity or not budget:
            return "Please fill out all fields", 400
    
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a travel expert that will give people wonderful and original travel ideas. You sound warm and not like AI. Try to give precise recommendations for places eg cafes, restaurants, shops"},
                {
                    "role": "user",
                    "content": f"Give me a relatively short travel recommendation for the user based on four parameters that I will provide - location: {location}, mood: {mood}, activity: {activity}, budget: {budget}. Return this in a json format. Like so: ```(\"recommendation\": \"value\")" 
                }
            ]
        )

       
        response_string = completion.choices[0].message.content
        
        start_index = response_string.find('{')
        end_index = response_string.rfind('}') + 1
        json_string = response_string[start_index:end_index]


        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            print("FAILED")

        mood_keywords = {
        'adventurous': ['upbeat', 'epic', 'adventure', 'exciting'],
        'relaxed': ['chill', 'relaxing', 'mellow', 'laid back'],
        'romantic': ['love', 'romantic', 'date night', 'romance'],
        'energetic': ['workout', 'energy', 'pump up', 'high energy'],
        'peaceful': ['calm', 'peaceful', 'meditation', 'tranquil']
        }
    
        activity_keywords = {
        'outdoor': ['nature', 'adventure', 'hiking', 'travel'],
        'cultural': ['world music', 'cultural', 'traditional'],
        'culinary': ['dinner', 'cooking', 'lounge', 'cafe'],
        'entertainment': ['party', 'fun', 'celebration'],
        'wellness': ['spa', 'yoga', 'meditation', 'wellness']
        }

        mood_term = random.choice(mood_keywords.get(mood.lower(), [mood]))
        activity_term = random.choice(activity_keywords.get(activity.lower(), [activity]))

        search_query = f"{mood_term} {activity_term}"

        result = sp.search(q=search_query, type="playlist", limit=10)
        playlistIds = []

        for playlist in result['playlists']['items']:
            if playlist and playlist['id']:
                playlistIds.append(playlist['id'])

        random_item = random.choice(playlistIds)
    
        
        return render_template("answer.html", recommendation=data["recommendation"], spotify_playlist_id=random_item, mood=mood)

    return render_template("questions.html")

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    response = redirect(url_for("login"))
    response.delete_cookie("email")

    return response

@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":

        db = get_db()
        email = request.form.get("email").strip()

         # Check if email is empty
        if not email:
            return "Email field cannot be empty!", 400
        
        random_letters = []
        
        for _ in range(4): 
            random_letters.append(random.choice(string.ascii_letters))

        random_letters_str = "".join(random_letters)

        user = db.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,)).fetchone()

        if user:
            user_id = user[0]
        else:
            return "Email was not found!", 404

        db.execute("INSERT INTO codes (code, user_id) VALUES (?, ?)", (random_letters_str, user_id))
        db.commit()
        
        r = resend.Emails.send({
            "from": "noreply@wanderlist.ancibk.com",
            "to": email,
            "subject": "Forgotten password",
            "html": f"<div><p>Change your password !</p><p>Your reset code is: {random_letters_str}</p></div>"
            })

        return redirect(url_for("reset"))
    return render_template("forgot.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        db = get_db()

        reset_code = request.form.get("code")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password == confirmation:
            hashed_password = generate_password_hash(password)
        else:
            return "Passwords do not match.", 400
            
        code_entry = db.execute("SELECT user_id FROM codes WHERE code = ?", (reset_code,)).fetchone()

        if code_entry:
            user_id = code_entry["user_id"]
    
            db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
            db.commit()

            db.execute("DELETE FROM codes WHERE code = ?", (reset_code,))
            db.commit()

            return redirect("/")
        else:
            return "Invalid code. Please try again", 400
    
    return render_template("reset.html")


if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
