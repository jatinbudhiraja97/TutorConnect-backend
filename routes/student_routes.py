from flask import Blueprint, request, jsonify
from models import Student, Booking, Notification
from utils.jwt_utils import decode_jwt

student_routes = Blueprint('student_routes', __name__)

@student_routes.route('/student_profile', methods=['GET'])
def student_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1]
    user_id = decode_jwt(token)
    
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"message": "Student profile not found"}), 404

    return jsonify({
        "name": student.name,
        "profile_picture": None,
        "subjects": student.subjects
    })

@student_routes.route('/student_history', methods=['GET'])
def student_history():
    token = request.cookies.get('token')
    user_id = decode_jwt(token)
    
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    history = Booking.query.filter_by(student_id=user_id).all()
    return jsonify([{
        "professor_name": booking.professor.name,
        "date": booking.date,
        "time": booking.time
    } for booking in history])

@student_routes.route('/student_notifications', methods=['GET'])
def student_notifications():
    token = request.cookies.get('token')
    user_id = decode_jwt(token)
    
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    notifications = Notification.query.filter_by(student_id=user_id).all()
    return jsonify([{
        "title": notification.title,
        "message": notification.message,
        "date": notification.date
    } for notification in notifications])
