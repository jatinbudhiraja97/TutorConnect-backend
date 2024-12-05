from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import secrets

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Generate a secure secret key for session management
    app.secret_key = secrets.token_hex(24)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost:5432/mydatabase'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import auth_routes, professor_routes, student_routes, booking_routes, rating_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(professor_routes.bp)
    app.register_blueprint(student_routes.bp)
    app.register_blueprint(booking_routes.bp)
    app.register_blueprint(rating_routes.bp)

    return app
