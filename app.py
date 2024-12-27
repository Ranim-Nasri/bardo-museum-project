from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, Category, Feedback, QuizQuestion, Room, User
from datetime import datetime
from random import sample
from flask_cors import CORS
import requests, os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

API_KEY = 'AIzaSyBVezeNR4Dn_K1ETIrnBJnDy9iyIKVc-bE'  
CX = '642ef41d594bc4032'

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bardo_museum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Ranim*9*Nasri'
CORS(app) 


db.init_app(app)

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/auth')
    return render_template('index.html')


@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/categories-page')
def categories_page():
    try:
        categories = Category.query.all()
        return render_template('categories.html', categories=categories)
    except SQLAlchemyError as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/')
def authentication():
    return render_template('auth.html')


    
@app.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        
        if isinstance(data, list):
            categories = []
            for item in data:
                category = Category(
                    category_name=item.get('category_name'),
                    description=item.get('description'),
                    num_exhibits=item.get('num_exhibits')
                )
                categories.append(category)
            db.session.add_all(categories)
        else:
            
            category = Category(
                category_name=data.get('category_name'),
                description=data.get('description'),
                num_exhibits=data.get('num_exhibits')
            )
            db.session.add(category)

        db.session.commit()
        return jsonify({"message": "Categories added successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category with the same name already exists."}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.json
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        if 'category_name' in data:
            category.category_name = data['category_name']
        if 'description' in data:
            category.description = data['description']
        if 'num_exhibits' in data:
            category.num_exhibits = data['num_exhibits']

        db.session.commit()
        return jsonify({"message": "Category updated successfully", "category": category.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category with the same name already exists."}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = Category.query.get(category_id)

        if not category:
            return jsonify({"error": "Category not found"}), 404

        return jsonify(category.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/feedback', methods=['POST'])
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


@app.route('/feedback', methods=['GET'])
def get_feedback():
    try:
        feedback_entries = Feedback.query.all()
        
        feedback_list = [feedback.to_dict() for feedback in feedback_entries]

        return jsonify(feedback_list), 200
    except SQLAlchemyError as e:
        
        return jsonify({"error": str(e)}), 500
@app.route('/quiz_questions', methods=['POST'])
def add_quiz_question():
    data = request.json

    if not data:
        return jsonify({"error": "Invalid input. No data provided."}), 400

    try:
        # Extracting data for the question
        question_text = data.get('question_text')
        option_a = data.get('option_a')
        option_b = data.get('option_b')
        option_c = data.get('option_c')
        option_d = data.get('option_d')
        correct_option = data.get('correct_option')

        # Validating the input data
        if not all([question_text, option_a, option_b, option_c, option_d, correct_option]):
            return jsonify({"error": "All fields are required."}), 400
        if correct_option not in ['a', 'b', 'c', 'd']:
            return jsonify({"error": "Correct option must be one of 'a', 'b', 'c', 'd'."}), 400

        # Creating a new QuizQuestion instance
        quiz_question = QuizQuestion(
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option
        )

        # Adding and committing to the database
        db.session.add(quiz_question)
        db.session.commit()

        return jsonify({"message": "Quiz question added successfully!", "question": quiz_question.to_dict()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/quiz_questions', methods=['GET'])
def get_all_quiz_questions():
    try:
        questions = QuizQuestion.query.all()
        return jsonify([question.to_dict() for question in questions]), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/quiz_questions/<int:question_id>', methods=['GET'])
def get_quiz_question(question_id):
    try:
        question = QuizQuestion.query.get(question_id)
        if not question:
            return jsonify({"error": "Quiz question not found"}), 404
        return jsonify(question.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
@app.route('/quiz_questions/<int:question_id>', methods=['PUT'])
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
@app.route('/quiz_questions/<int:question_id>', methods=['DELETE'])
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
@app.route('/quiz_questions', methods=['GET'])
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
    
def fetch_google_data(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Debugging the response
        print("Google API response:", data)
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Google: {e}")
        return None




# Route to fetch Google Search data based on category
@app.route('/fetch-google-info/<category_name>', methods=['GET'])
def fetch_google_info(category_name):
    search_query = f"{category_name} Bardo Museum"
    google_data = fetch_google_data(search_query)
    if google_data and 'items' in google_data:
        print(f"Searching for: {search_query}")
        results = google_data['items']
        return jsonify(results), 200
        
    else:
        return jsonify({"error": "No information found."}), 404

@app.route('/rooms', methods=['POST'])
def add_rooms():
    try:
        data = request.get_json()  # Get the JSON data from the request
        
        if isinstance(data, list):  # If it's a list of rooms
            rooms = []  # A list to hold Room instances
            for room in data:
                new_room = Room(
                    name=room["name"],
                    level=room["level"],
                    type=room["type"],
                    connections_list=room["connections"]  # Use connections_list setter
                )
                rooms.append(new_room)  # Add the room to the list
            db.session.add_all(rooms)  # Add all rooms in one go to the database
        else:  # If it's a single room
            new_room = Room(
                name=data["name"],
                level=data["level"],
                type=data["type"],
                connections_list=data["connections"]  # Use connections_list setter
            )
            db.session.add(new_room)  # Add the single room to the database

        db.session.commit()  # Commit the transaction
        return jsonify({"message": "Rooms added successfully"}), 201  # Return a success message

    except Exception as e:
        db.session.rollback()  # Rollback the transaction if there's an error
        return jsonify({"error": str(e)}), 400  # Return the error message

@app.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()  # Fetch all rooms from the database
    # Return the room details in JSON format
    return jsonify([{
        "id": room.id,
        "name": room.name,
        "level": room.level,
        "type": room.type,
        "connections": room.connections
    } for room in rooms]), 200

@app.route('/rooms/<int:room_id>/connections', methods=['GET'])
def get_room_connections(room_id):
    try:
        room = Room.query.get(room_id)
        if room:
            connections = room.connections_list  # Assuming `connections_list` gives a list of connected room names
            return jsonify(connections), 200
        else:
            return jsonify({"error": "Room not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    try:
        room = Room.query.get(room_id)  # Fetch the room from the database by ID

        if room:
            return jsonify({
                "id": room.id,
                "name": room.name,
                "level": room.level,
                "type": room.type,
                "connections": room.connections
            }), 200
        else:
            return jsonify({"error": "Room not found"}), 404  # Room not found

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Server error


@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    try:
        # Get the data to update the room
        data = request.get_json()

        # Find the room to update
        room = Room.query.get(room_id)

        if not room:
            return jsonify({"error": "Room not found"}), 404

        # Update room attributes
        room.name = data.get("name", room.name)
        room.level = data.get("level", room.level)
        room.type = data.get("type", room.type)
        room.connections_list = data.get("connections", room.connections_list)

        # Commit the changes
        db.session.commit()
        return jsonify({"message": "Room updated successfully", "room": room.name}), 200

    except Exception as e:
        db.session.rollback()  # Rollback the transaction if there's an error
        return jsonify({"error": str(e)}), 400  # Return the error message

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    try:
        # Find the room to delete
        room = Room.query.get(room_id)

        if not room:
            return jsonify({"error": "Room not found"}), 404

        # Delete the room
        db.session.delete(room)
        db.session.commit()
        return jsonify({"message": "Room deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()  # Rollback the transaction if there's an error
        return jsonify({"error": str(e)}), 400  # Return the error message

@app.route('/auth/signup', methods=['POST'])
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
        session.permanent = False  # Session expires when browser closes
        return jsonify({'message': 'Successfully registered'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/auth/signin', methods=['POST'])
def signin():
    data = request.json
    try:
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
            
        if check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            session.permanent = False  # Session expires when browser closes
            return jsonify({'message': 'Successfully logged in'}), 200
        
        return jsonify({'error': 'Invalid email or password'}), 401
    
    except Exception as e:
        print("Error during signin:", e)  # Debugging
        return jsonify({'error': str(e)}), 500




@app.route('/user', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        } for user in users]), 200
    except SQLAlchemyError as e:
        print("Database error:", str(e))  # Debug print
        return jsonify({'error': 'Database error'}), 500

@app.route('/user/<int:user_id>', methods=['DELETE'])
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
            'message': 'User account deleted successfully',
            'redirect': '/auth'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
if __name__ == "__main__":
    with app.app_context():
       
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully.")
        

    app.run(debug=True)
