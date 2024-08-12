from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Student, Professor
from extensions import db
from utils.jwt_utils import generate_jwt, decode_jwt

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    role = data.get('role')
    password = data.get('password')

    if not name or not email or not role or not password:
        return jsonify({"message": "Missing required fields"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists!"}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    new_user = User(email=email, password=hashed_password, role=role, name=name)
    db.session.add(new_user)
    db.session.flush()  # Flush to get the user_id

    if role == 'student':
        new_student = Student(user_id=new_user.id, name=name, subjects=data.get('subjects', ''))
        db.session.add(new_student)
    elif role == 'professor':
        new_professor = Professor(
            user_id=new_user.id, 
            name=name, 
            department=data.get('department', ''), 
            experience=data.get('experience', 0), 
            subjects=data.get('subjects', ''),
            academics=data.get('academics', ''),
            profile_picture=data.get('profile_picture', '')
        )
        db.session.add(new_professor)

    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], role=data['role']).first()

    if user and check_password_hash(user.password, data['password']):
        token = generate_jwt(user.id)
        response = jsonify({"message": "Login successful", "token": token})
        return response
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@auth_routes.route('/validate_token', methods=['GET'])
def validate_token():
    token = request.headers.get('Authorization', '').split(' ')[1]
    user_id = decode_jwt(token)

    if not user_id:
        return jsonify({"valid": False}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"valid": False}), 404

    return jsonify({"valid": True, "name": user.name}), 200
