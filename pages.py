from flask import Blueprint, render_template, redirect, session, url_for
from models import Category
from sqlalchemy.exc import SQLAlchemyError

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def landing():
    return render_template('index.html')

@pages_bp.route('/auth')
def auth():
    return render_template('auth.html')

@pages_bp.route('/create')
def create():
    return render_template('create.html')

@pages_bp.route('/map')
def map_page():
    return render_template('map.html')

@pages_bp.route('/rate')
def rate():
    if 'user_id' not in session:
        return redirect(url_for('pages.auth'))
    return render_template('rate.html')

@pages_bp.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('pages.auth'))
    return render_template('index.html')

@pages_bp.route('/categories-page')
def categories_page():
    try:
        categories = Category.query.all()
        return render_template('categories.html', categories=categories)
    except SQLAlchemyError as e:
        return f"An error occurred: {str(e)}"