from flask import Blueprint, request, jsonify
from models import QuizQuestion, db
from sqlalchemy.exc import SQLAlchemyError
from random import sample

quiz_questions_bp = Blueprint('quiz_questions', __name__, url_prefix='/quiz_questions')

@quiz_questions_bp.route('/', methods=['GET'])
def get_all_quiz_questions():
    try:
        questions = QuizQuestion.query.all()
        return jsonify([question.to_dict() for question in questions]), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@quiz_questions_bp.route('/', methods=['POST'])
def add_quiz_question():
    data = request.json

    if not data:
        return jsonify({"error": "Invalid input. No data provided."}), 400

    def validate_and_create_question(question_data):
        question_text = question_data.get('question_text')
        option_a = question_data.get('option_a')
        option_b = question_data.get('option_b')
        option_c = question_data.get('option_c')
        option_d = question_data.get('option_d')
        correct_option = question_data.get('correct_option')

        if not all([question_text, option_a, option_b, option_c, option_d, correct_option]):
            return None, "All fields are required."

        if correct_option not in ['a', 'b', 'c', 'd']:
            return None, "Correct option must be one of 'a', 'b', 'c', 'd'."

        return QuizQuestion(
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option
        ), None

    if isinstance(data, dict):  # Single question
        data = [data]  # Convert to list for uniform processing

    created_questions = []
    for question_data in data:
        quiz_question, error = validate_and_create_question(question_data)
        if error:
            return jsonify({"error": error}), 400

        db.session.add(quiz_question)
        created_questions.append(quiz_question.to_dict())

    try:
        db.session.commit()
        return jsonify({"message": "Quiz questions added successfully!", "questions": created_questions}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@quiz_questions_bp.route('/<int:question_id>', methods=['GET'])
def get_quiz_question(question_id):
    try:
        question = QuizQuestion.query.get(question_id)
        if not question:
            return jsonify({"error": "Quiz question not found"}), 404
        return jsonify(question.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    

@quiz_questions_bp.route('/<int:question_id>', methods=['PUT'])
def update_quiz_question(question_id):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input. No data provided."}), 400

    try:
        question = QuizQuestion.query.get(question_id)
        if not question:
            return jsonify({"error": "Quiz question not found"}), 404

        # Updating fields if present in the request
        if 'question_text' in data:
            question.question_text = data['question_text']
        if 'option_a' in data:
            question.option_a = data['option_a']
        if 'option_b' in data:
            question.option_b = data['option_b']
        if 'option_c' in data:
            question.option_c = data['option_c']
        if 'option_d' in data:
            question.option_d = data['option_d']
        if 'correct_option' in data:
            if data['correct_option'] not in ['a', 'b', 'c', 'd']:
                return jsonify({"error": "Correct option must be one of 'a', 'b', 'c', 'd'."}), 400
            question.correct_option = data['correct_option']

        db.session.commit()
        return jsonify({"message": "Quiz question updated successfully!", "question": question.to_dict()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@quiz_questions_bp.route('/<int:question_id>', methods=['DELETE'])
def delete_quiz_question(question_id):
    try:
        question = QuizQuestion.query.get(question_id)
        if not question:
            return jsonify({"error": "Quiz question not found"}), 404

        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Quiz question deleted successfully!"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@quiz_questions_bp.route('/', methods=['GET'])
def get_quiz_questions():
    try:
        # Get all questions from database
        questions = QuizQuestion.query.all()
        # Convert to list of dictionaries
        selected_questions = sample(questions, min(10, len(questions)))
        questions_list = [question.to_dict() for question in selected_questions]
        return jsonify(questions_list), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500