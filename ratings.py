from flask import Blueprint, request, jsonify, session
from models import Rating, db
from sqlalchemy import func
from datetime import datetime

ratings_bp = Blueprint('ratings', __name__, url_prefix='/ratings')

@ratings_bp.route('/', methods=['POST'])
def submit_rating():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Please sign in to submit ratings'
        }), 401

    try:
        data = request.get_json()
        if not data or 'ratings' not in data or 'feedback' not in data:
            return jsonify({
                'success': False,
                'message': 'Rating data and feedback are required'
            }), 400

        user_id = session['user_id']

        # Assume you want to allow one rating per user forever:
        print(f"Session User ID: {session.get('user_id')}")
        existing_rating = Rating.query.filter_by(user_id=user_id).first()
        if existing_rating:
            print(f"Found existing rating for user ID {user_id}: {existing_rating.id}")
            return jsonify({'success': False, 'message': 'You have already submitted your rating.'}), 400
        else:
            print("No existing rating found, proceeding to create a new one.")

        # Create new rating entry
        new_rating = Rating(
            user_id=user_id,
            exhibits_rating=data['ratings'].get('exhibits'),
            map_rating=data['ratings'].get('map'),
            tour_rating=data['ratings'].get('tour'),
            audio_rating=data['ratings'].get('audio'),
            quiz_rating=data['ratings'].get('quiz'),
            mosaic_rating=data['ratings'].get('mosaic'),
            exhibits_feedback=data['feedback'].get('exhibits', ''),
            map_feedback=data['feedback'].get('map', ''),
            tour_feedback=data['feedback'].get('tour', ''),
            audio_feedback=data['feedback'].get('audio', ''),
            quiz_feedback=data['feedback'].get('quiz', ''),
            mosaic_feedback=data['feedback'].get('mosaic', ''),
            created_at=datetime.utcnow()
        )

        db.session.add(new_rating)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully',
            'summary': new_rating.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@ratings_bp.route('/summary', methods=['GET'])
def get_rating_summary():
    try:
        summary = db.session.query(
            func.avg(Rating.exhibits_rating).label('avg_exhibits'),
            func.avg(Rating.map_rating).label('avg_map'),
            func.avg(Rating.tour_rating).label('avg_tour'),
            func.avg(Rating.audio_rating).label('avg_audio'),
            func.avg(Rating.quiz_rating).label('avg_quiz'),
            func.avg(Rating.mosaic_rating).label('avg_mosaic'),
            func.count(Rating.id).label('total_ratings')
        ).first()

        # Ensure this returns a dictionary, not a Response object
        return {
            'exhibits': round(float(summary.avg_exhibits or 0), 1),
            'map': round(float(summary.avg_map or 0), 1),
            'tour': round(float(summary.avg_tour or 0), 1),
            'audio': round(float(summary.avg_audio or 0), 1),
            'quiz': round(float(summary.avg_quiz or 0), 1),
            'mosaic': round(float(summary.avg_mosaic or 0), 1),
            'total_ratings': summary.total_ratings
        }

    except Exception as e:
        # Ensure the error response is also a dictionary
        return {
            'success': False,
            'message': str(e)
        }, 500

@ratings_bp.route('/feedback', methods=['GET'])
def get_recent_feedback():
    try:
        # Get recent feedback entries
        recent_feedback = Rating.query\
            .filter(db.or_(
                Rating.exhibits_feedback != None,
                Rating.map_feedback != None,
                Rating.tour_feedback != None,
                Rating.audio_feedback != None,
                Rating.quiz_feedback != None,
                Rating.mosaic_feedback != None
            ))\
            .order_by(Rating.created_at.desc())\
            .limit(10)\
            .all()
            
        return jsonify({
            'success': True,
            'data': [rating.to_dict() for rating in recent_feedback]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

