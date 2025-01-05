from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from models import db
from sentiment import sentiment_analysis_api
from auth import auth_bp
from categories import categories_bp
from feedback import feedback_bp
from quiz_questions import quiz_questions_bp
from rooms import rooms_bp
from google_search import google_bp
from ratings import ratings_bp
from pages import pages_bp

def create_app():
    app = Flask(__name__)
    
    # Configurations
    app.config["API_TITLE"] = "Bardo Museum REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:Postgres25@localhost/Bardo Museum'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = 'Ranim*9*Nasri'
    app.config["PROPAGATE_EXCEPTIONS"] = True



    # Extensions
    CORS(app)
    db.init_app(app)
    api = Api(app)
    
    # Register blueprints
    app.register_blueprint(sentiment_analysis_api, url_prefix='/api')
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(quiz_questions_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(google_bp) 
    app.register_blueprint(ratings_bp)
    app.register_blueprint(pages_bp)

    with app.app_context():
        db.create_all()

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=True,
        ssl_context=(
            '127.0.0.1.pem',  # Path to SSL certificate
            '127.0.0.1-key.pem'  # Path to private key
        )
    )
