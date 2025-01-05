from flask import Blueprint, request, jsonify
from models import Feedback, db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('/', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Convert visit_date from string to a Python date object
        visit_date = datetime.strptime(data.get('visit_date'), '%Y-%m-%d').date()

        feedback = Feedback(
            visitor_name=data.get('visitor_name'),
            visit_date=visit_date,
            feedback_text=data.get('feedback_text')
        )

        db.session.add(feedback)
        db.session.commit()
        return jsonify({"message": "Feedback submitted successfully", "feedback": feedback.to_dict()}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Duplicate feedback is not allowed."}), 409
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@feedback_bp.route('/', methods=['GET'])
def get_feedback():
    try:
        feedback_entries = Feedback.query.all()
        
        feedback_list = [feedback.to_dict() for feedback in feedback_entries]

        return jsonify(feedback_list), 200
    except SQLAlchemyError as e:
        
        return jsonify({"error": str(e)}), 500