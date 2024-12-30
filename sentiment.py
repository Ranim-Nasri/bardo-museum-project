from flask import Blueprint, jsonify, request
from models import db, Rating
from textblob import TextBlob
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import func
import numpy as np

sentiment_analysis_api = Blueprint('sentiment_analysis_api', __name__)

def analyze_sentiment(feedback_text):
    """Returns sentiment polarity and subjectivity scores"""
    if not feedback_text:
        return 0.0, 0.0
    blob = TextBlob(str(feedback_text))
    return blob.sentiment.polarity, blob.sentiment.subjectivity

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
    """Returns sentiment polarity score (only polarity)"""
    if not feedback_text:
        return 0.0  # Returning only polarity
    blob = TextBlob(str(feedback_text))
    return blob.sentiment.polarity  # Only polarity is returned

# Function to categorize sentiment
def categorize_sentiment(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# Sentiment analysis endpoint

# Original endpoint for overall sentiment analysis
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

# New endpoint for detailed feedback analysis
@sentiment_analysis_api.route('/analyze/detailed', methods=['GET'])
def get_detailed_analysis():
    try:
        ratings = Rating.query.all()
        detailed_analysis = defaultdict(list)

        for rating in ratings:
            for feature in ['exhibits', 'map', 'tour', 'audio', 'quiz', 'mosaic']:
                feedback = getattr(rating, f'{feature}_feedback')
                rating_value = getattr(rating, f'{feature}_rating')

                if feedback:
                    polarity = analyze_sentiment(feedback)  # Only polarity, no unpacking
                    detailed_analysis[feature].append({
                        'feedback': feedback,
                        'sentiment_score': round(polarity, 2),
                        'rating': rating_value,
                        'category': categorize_sentiment(polarity),
                        'timestamp': rating.created_at.isoformat() if hasattr(rating, 'created_at') and rating.created_at else None
                    })

        return jsonify({
            "success": True,
            "detailed_analysis": dict(detailed_analysis)  # Convert defaultdict to regular dict
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@sentiment_analysis_api.route('/analyze/trends', methods=['GET'])
def get_sentiment_trends():
    try:
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        ratings = Rating.query.filter(Rating.created_at >= start_date).all()
        trends = defaultdict(lambda: defaultdict(list))
        
        for rating in ratings:
            if not hasattr(rating, 'created_at') or not rating.created_at:
                continue
                
            date_str = rating.created_at.strftime('%Y-%m-%d')
            
            for feature in ['exhibits', 'map', 'tour', 'audio', 'quiz', 'mosaic']:
                feedback = getattr(rating, f'{feature}_feedback')
                if feedback:
                    polarity = analyze_sentiment(feedback)  # No unpacking here, only polarity
                    trends[feature][date_str].append(polarity)
        
        # Calculate daily averages
        averaged_trends = {}
        for feature, dates in trends.items():
            averaged_trends[feature] = {
                date: round(sum(scores) / len(scores), 2)
                for date, scores in dates.items()
            }
        
        return jsonify({
            "success": True,
            "trends": averaged_trends
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@sentiment_analysis_api.route('/analyze/keywords', methods=['GET'])
def get_keyword_analysis():
    try:
        ratings = Rating.query.all()
        keyword_analysis = defaultdict(lambda: defaultdict(list))
        
        positive_keywords = ['great', 'excellent', 'amazing', 'good', 'love', 'fantastic']
        negative_keywords = ['poor', 'bad', 'terrible', 'disappointing', 'issues', 'problem']
        
        for rating in ratings:
            for feature in ['exhibits', 'map', 'tour', 'audio', 'quiz', 'mosaic']:
                feedback = getattr(rating, f'{feature}_feedback')
                if feedback and isinstance(feedback, str):  # Ensure feedback is a string
                    feedback_lower = feedback.lower()
                    
                    for keyword in positive_keywords + negative_keywords:
                        if keyword in feedback_lower:
                            polarity = analyze_sentiment(feedback)  # No unpacking here, only polarity
                            keyword_analysis[feature][keyword].append({
                                'sentiment': round(polarity, 2),
                                'feedback': feedback
                            })
        
        # Convert defaultdict to regular dict for JSON serialization
        return jsonify({
            "success": True,
            "keyword_analysis": {
                feature: dict(keywords) 
                for feature, keywords in keyword_analysis.items()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@sentiment_analysis_api.route('/analyze/compare', methods=['GET'])
def get_comparative_analysis():
    try:
        ratings = Rating.query.all()
        comparative_data = defaultdict(lambda: {
            'sentiment_scores': [],
            'rating_scores': [],
            'correlation': None,
            'average_sentiment': 0,
            'average_rating': 0
        })
        
        for rating in ratings:
            for feature in ['exhibits', 'map', 'tour', 'audio', 'quiz', 'mosaic']:
                feedback = getattr(rating, f'{feature}_feedback')
                rating_value = getattr(rating, f'{feature}_rating')
                
                if feedback and rating_value:
                    polarity = analyze_sentiment(feedback)  # No unpacking here, only polarity
                    comparative_data[feature]['sentiment_scores'].append(polarity)
                    comparative_data[feature]['rating_scores'].append(float(rating_value))
        
        # Calculate statistics
        for feature, data in comparative_data.items():
            if data['sentiment_scores'] and data['rating_scores']:
                data['average_sentiment'] = round(float(np.mean(data['sentiment_scores'])), 2)
                data['average_rating'] = round(float(np.mean(data['rating_scores'])), 2)
                
                if len(data['sentiment_scores']) > 1:  # Need at least 2 points for correlation
                    correlation = np.corrcoef(data['sentiment_scores'], data['rating_scores'])
                    data['correlation'] = round(float(correlation[0, 1]), 2)
                else:
                    data['correlation'] = None
                
                # Clean up the response
                del data['sentiment_scores']
                del data['rating_scores']
        
        return jsonify({
            "success": True,
            "comparative_analysis": dict(comparative_data)  # Convert defaultdict to regular dict
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
