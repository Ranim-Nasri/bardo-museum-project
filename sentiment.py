from flask import Blueprint, jsonify
from models import db, Rating  # Import app and db from app.py
from textblob import TextBlob

# Create a blueprint for sentiment analysis routes
sentiment_analysis_api = Blueprint('sentiment_analysis_api', __name__)

# Function to fetch feedback data
def fetch_feedback_data():
    ratings = Rating.query.all()
    feedback_data = {
        "exhibits": [],
        "map": [],
        "tour": [],
        "audio": [],
        "quiz": [],
        "mosaic": []
    }
    for rating in ratings:
        feedback_data["exhibits"].append(rating.exhibits_feedback)
        feedback_data["map"].append(rating.map_feedback)
        feedback_data["tour"].append(rating.tour_feedback)
        feedback_data["audio"].append(rating.audio_feedback)
        feedback_data["quiz"].append(rating.quiz_feedback)
        feedback_data["mosaic"].append(rating.mosaic_feedback)
    return feedback_data

# Function to analyze sentiment
def analyze_sentiment(feedback_text):
    blob = TextBlob(feedback_text)
    return blob.sentiment.polarity  # Polarity ranges from -1 (negative) to 1 (positive)

# Function to categorize sentiment
def categorize_sentiment(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# Sentiment analysis endpoint
@sentiment_analysis_api.route('/sentiment-analysis', methods=['GET'])
def get_sentiment_analysis():
    feedback_data = fetch_feedback_data()

    feedback_analysis = {}
    for section, feedback_list in feedback_data.items():
        feedback_analysis[section] = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        for feedback in feedback_list:
            if feedback:  # Check if feedback is not empty
                score = analyze_sentiment(feedback)
                sentiment_category = categorize_sentiment(score)
                feedback_analysis[section][sentiment_category.lower()] += 1

    # Return the analysis results as JSON
    return jsonify(feedback_analysis)
