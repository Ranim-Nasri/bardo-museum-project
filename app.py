from flask import Flask, render_template, request, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, Category, Feedback
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bardo_museum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')


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



if __name__ == "__main__":
    with app.app_context():
       
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully.")
    app.run(debug=True)
