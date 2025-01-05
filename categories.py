from flask import Blueprint, request, jsonify
from models import Category, db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = Category.query.get(category_id)

        if not category:
            return jsonify({"error": "Category not found"}), 404

        return jsonify(category.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/', methods=['POST'])
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


@categories_bp.route('/<int:category_id>', methods=['PUT'])
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

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
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