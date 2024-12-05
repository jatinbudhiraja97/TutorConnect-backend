from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Student, Professor
from app.utils.jwt_utils import generate_jwt

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    # Signup logic
    ...

@bp.route('/login', methods=['POST'])
def login():
    # Login logic
    ...
