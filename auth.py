from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        new_user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            full_name=data['name']
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session.permanent = False
        return jsonify({'message': 'Successfully registered'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.json
    try:
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        if check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            session.permanent = False
            return jsonify({'message': 'Successfully logged in'}), 200
        return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        print("Error during signin:", e)
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['GET'])  
def logout():
    session.pop('user_id', None)
    return redirect(url_for('pages.landing') + "?logged_out=true")

@auth_bp.route('/users', methods=['GET'])  # Changed route to be more RESTful
def get_users():
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        } for user in users]), 200
    except SQLAlchemyError as e:
        print("Database error:", str(e))
        return jsonify({'error': 'Database error'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])  # Changed route to be more RESTful
def delete_user_by_id(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    if session['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized to delete this account'}), 403
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return jsonify({
            'message': 'User account deleted successfully'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500