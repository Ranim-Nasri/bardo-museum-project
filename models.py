from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    num_exhibits = db.Column(db.Integer, nullable=False)

    def __init__(self, category_name, description, num_exhibits):
        self.category_name = category_name
        self.description = description
        self.num_exhibits = num_exhibits

    def to_dict(self):
        return {
            "id": self.id,
            "category_name": self.category_name,
            "description": self.description,
            "num_exhibits": self.num_exhibits
           
        }
    
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitor_name = db.Column(db.String(100), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    
    
    __table_args__ = (
        db.UniqueConstraint('visitor_name', 'visit_date', 'feedback_text', name='unique_feedback'),
    )

    def __init__(self, visitor_name, visit_date, feedback_text):
        self.visitor_name = visitor_name
        self.visit_date = visit_date
        self.feedback_text = feedback_text

    def to_dict(self):
        return {
            "id": self.id,
            "visitor_name": self.visitor_name,
            "visit_date": self.visit_date.isoformat(),
            "feedback_text": self.feedback_text,
        }
    

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False) 

    def __init__(self, question_text, option_a, option_b, option_c, option_d, correct_option):
        self.question_text = question_text
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.correct_option = correct_option

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "options": {
                "a": self.option_a,
                "b": self.option_b,
                "c": self.option_c,
                "d": self.option_d
            },
            "correct_option": self.correct_option
        }
import json


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'exhibit', 'service', 'pathway'
    connections = db.Column(db.String(200), nullable=False)  # Connections to other rooms

    def __repr__(self):
        return f"<Room {self.name} (Level {self.level})>"

    @property
    def connections_list(self):
        """Deserialize the connections string into a list."""
        return json.loads(self.connections)

    @connections_list.setter
    def connections_list(self, value):
        """Serialize the list of connections into a string."""
        self.connections = json.dumps(value)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('ratings', lazy=True, cascade='all, delete-orphan'))
    # Ratings for each section (1-5 stars)
    exhibits_rating = db.Column(db.Integer)
    map_rating = db.Column(db.Integer)
    tour_rating = db.Column(db.Integer)
    audio_rating = db.Column(db.Integer)
    quiz_rating = db.Column(db.Integer)
    mosaic_rating = db.Column(db.Integer)
    
    # Feedback text for each section
    exhibits_feedback = db.Column(db.Text)
    map_feedback = db.Column(db.Text)
    tour_feedback = db.Column(db.Text)
    audio_feedback = db.Column(db.Text)
    quiz_feedback = db.Column(db.Text)
    mosaic_feedback = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,  # Include user_id in the dictionary for response
            'ratings': {
                'exhibits': self.exhibits_rating,
                'map': self.map_rating,
                'tour': self.tour_rating,
                'audio': self.audio_rating,
                'quiz': self.quiz_rating,
                'mosaic': self.mosaic_rating
            },
            'feedback': {
                'exhibits': self.exhibits_feedback,
                'map': self.map_feedback,
                'tour': self.tour_feedback,
                'audio': self.audio_feedback,
                'quiz': self.quiz_feedback,
                'mosaic': self.mosaic_feedback
            },
            'created_at': self.created_at.isoformat()
        }