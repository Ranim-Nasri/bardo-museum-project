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