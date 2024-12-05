from flask import Blueprint, jsonify, request
from app import db
from app.models import Student, Notification, Booking
from app.utils.jwt_utils import decode_jwt

bp = Blueprint('students', __name__)

@bp.route('/student_profile', methods=['GET'])
def student_profile():
    token = request.headers.get('Authorization', None)
    if not token:
        return jsonify({"message": "Authorization header missing"}), 401

    token = token.split(" ")[1]
    user_id = decode_jwt(token)
    
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"message": "Student profile not found"}), 404

    return jsonify({
        "name": student.name,
        "profile_picture": student.profile_picture,
        "subjects": student.subjects
    })

@bp.route('/student_notifications', methods=['GET'])
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

@bp.route('/student_history', methods=['GET'])
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
