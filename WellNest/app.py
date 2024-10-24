from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
import random

app = Flask(__name__)

# Mood feedback messages dictionary
messages = {
    "Happy": [
        "We're glad you're feeling happy! Keep up the positivity!",
        "Happiness looks good on you! Share it with the world!",
        "You're radiating positive energy today—spread the joy!"
    ],
    "Sad": [
        "It's okay to feel sad sometimes. Take it easy and reach out to someone if you need support.",
        "Sad days happen. Be gentle with yourself, and know that brighter days are ahead.",
        "Take your time to process what you're feeling. You're not alone in this."
    ],
    "Anxious": [
        "Feeling anxious? Try some deep breathing or take a short walk to clear your mind.",
        "Anxiety can be tough, but remember, you've handled tough days before.",
        "It's okay to feel anxious. Focus on one small step at a time, and things will feel more manageable."
    ],
    "Neutral": [
        "Feeling neutral? That's perfectly fine! A balanced day can be a good day.",
        "Sometimes it's okay to just be. Take a moment to relax and reflect.",
        "Not feeling too high or low today? That’s a sign of balance—keep it steady!"
    ],
    "Excited": [
        "Excited? That's awesome! Share that energy with something creative or fun today!",
        "It’s great to see you excited! Use this energy to tackle something you’ve been looking forward to.",
        "You're buzzing with excitement—enjoy every moment and share the good vibes!"
    ],
    "Tired": [
        "Feeling tired? Make sure to get some rest. You deserve a break.",
        "It sounds like you could use some rest. Remember to take care of yourself.",
        "Feeling drained? Take a break and recharge. A little rest can go a long way."
    ],
    "Frustrated": [
        "Frustration happens. Take a moment to step away and come back with a fresh perspective.",
        "It’s okay to feel frustrated. Take deep breaths and approach the situation calmly when you're ready.",
        "Feeling stuck? Try to break things down into smaller pieces. One step at a time."
    ],
    "Grateful": [
        "Gratitude is a powerful thing! Keep holding on to that sense of thankfulness.",
        "Feeling grateful today? Let those around you know what they mean to you!",
        "What a wonderful feeling! Reflecting on what you're grateful for brings positivity."
    ],
    "Stressed": [
        "Feeling stressed? Try focusing on one small thing you can control right now.",
        "Stress can feel overwhelming. Take it slow, one task at a time.",
        "It's okay to feel stressed, but make sure to find a moment to breathe and reset."
    ]
}

# Map moods to numerical values
mood_map = {
    'Happy': 5,
    'Sad': 1,
    'Anxious': 2,
    'Neutral': 3,
    'Excited': 5,
    'Tired': 2,
    'Frustrated': 1,
    'Grateful': 5,
    'Stressed': 1
}

# Initialize the database
def initialize_db():
    with sqlite3.connect('moods.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mood_logs 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, mood TEXT, date TEXT)''')
        conn.commit()

# Log the mood into the database
def log_mood(mood):
    with sqlite3.connect('moods.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO mood_logs (mood, date) VALUES (?, ?)",
                  (mood.capitalize(), datetime.now().strftime('%Y-%m-%d')))
        conn.commit()

# Get mood history
def get_mood_history():
    with sqlite3.connect('moods.db') as conn:
        c = conn.cursor()
        c.execute("SELECT mood, date FROM mood_logs ORDER BY date DESC LIMIT 7")
        return c.fetchall()

# Clear mood history
def clear_mood_history():
    with sqlite3.connect('moods.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM mood_logs")
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        mood = request.form.get('mood')
        log_mood(mood)
        return redirect(url_for('thanks', mood=mood))

    # Prepare mood data for the chart
    mood_history = get_mood_history()
    mood_dates = [entry[1] for entry in mood_history]
    mood_values = [mood_map.get(entry[0], 0) for entry in mood_history]

    # Generate insights based on mood history
    insights = generate_insights(mood_history)

    return render_template("index.html", mood_dates=mood_dates, mood_values=mood_values, insights=insights)

def generate_insights(mood_history):
    if not mood_history:
        return ["Keep track of your mood regularly for better mental health."]

    mood_count = {}
    for mood, _ in mood_history:
        mood_count[mood] = mood_count.get(mood, 0) + 1

    most_common_mood = max(mood_count, key=mood_count.get)
    return [f"Your most common mood is {most_common_mood}. Keep it in mind!"]

@app.route('/reminders')
def reminders():
    return render_template('reminders.html')

@app.route('/selfcare')
def self_care():
    return render_template('selfcare.html')

@app.route('/thanks/<mood>')
def thanks(mood):
    mood_messages = messages.get(mood, ["Thank you for checking in!"])
    message = random.choice(mood_messages)
    return render_template('thanks.html', mood=mood, message=message)

@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST' and 'clear_history' in request.form:
        clear_mood_history()
        return redirect(url_for('history'))

    mood_history = get_mood_history()
    return render_template('history.html', mood_history=mood_history)

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/mood')
def mood_journal():
    return render_template('mood.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        bot_response = get_bot_response(user_input)
        return render_template('chat.html', user_input=user_input, bot_response = random.choice(bot_response))

    initial_message = "How are you feeling today? You can type 'happy', 'sad', 'anxious', or 'neutral'."
    return render_template('chat.html', bot_response=initial_message)

def get_bot_response(user_input):
    responses = {
        "happy": [
            "That's great to hear! What makes you happy?",
            "Keep smiling! 😊"
        ],
        "sad": [
            "I'm sorry to hear that. It's okay to feel sad. Would you like to talk about it?",
            "Take your time to feel better. 🌧️"
        ],
        "anxious": [
            "Anxiety can be tough. Have you tried any relaxation techniques?",
            "It's okay to feel anxious. Remember to breathe. 😟"
        ],
        "neutral": [
            "Sometimes being neutral is okay! How was your day?",
            "What do you usually do when you're feeling neutral? 😐"
        ],
        "tired": [
            "Feeling tired? It's okay to take a break and rest.",
            "Rest is important! What do you usually do to recharge? 💤"
        ],
        "frustrated": [
            "Feeling frustrated? It's okay to take a moment and step away.",
            "Try to focus on one small task at a time to reduce that frustration. 😠"
        ],
        "stressed": [
            "Stress can feel overwhelming. Try to take things one step at a time.",
            "It's okay to feel stressed. Remember to find moments to breathe and reset. 😣"
        ]
    }

    user_input_lower = user_input.lower()

    for keyword in responses.keys():
        if keyword in user_input_lower:
            return random.choice(responses[keyword])

    return random.choice(["I'm not sure how to respond to that. Can you tell me more?"])

if __name__ == "__main__":
    initialize_db()  # Call to create the database
    app.run(debug=True)
