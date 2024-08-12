from flask import Blueprint, request, jsonify
from models import Booking, Professor, Student
from utils.jwt_utils import decode_jwt
from extensions import db
import datetime

booking_routes = Blueprint('booking_routes', __name__)

@booking_routes.route('/book_appointment', methods=['POST'])
def book_appointment():
    token = request.headers.get('Authorization', None)

    if not token:
        return jsonify({"message": "Authorization header missing"}), 401

    token = token.split(" ")[1]
    student_id = decode_jwt(token)

    professor_id = request.json.get('professor_id')
    date = request.json.get('date')
    time = request.json.get('time')

    if not professor_id or not date or not time:
        return jsonify({"message": "Missing required fields"}), 400

    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    time_obj = datetime.datetime.strptime(time, '%I:%M %p').time()

    existing_booking = Booking.query.filter_by(professor_id=professor_id, date=date_obj, time=time_obj).first()

    if existing_booking:
        return jsonify({"message": "Time slot already booked"}), 409

    try:
        new_booking = Booking(
            student_id=student_id,
            professor_id=professor_id,
            date=date_obj,
            time=time_obj
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({"message": "Booking successful"}), 201

    except Exception as e:
        return jsonify({"message": f"Failed to create booking: {e}"}), 500

@booking_routes.route('/cancel_appointment/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    try:
        booking = Booking.query.get(appointment_id)
        if not booking:
            return jsonify({"message": "Booking not found"}), 404
        
        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking cancelled successfully"}), 200
    
    except Exception as e:
        return jsonify({"message": f"Failed to cancel booking: {e}"}), 500

@booking_routes.route('/reschedule_appointment/<int:appointment_id>', methods=['PUT'])
def reschedule_appointment(appointment_id):
    try:
        booking = Booking.query.get(appointment_id)
        if not booking:
            return jsonify({"message": "Booking not found"}), 404

        date = request.json.get('date')
        time = request.json.get('time')

        if not date or not time:
            return jsonify({"message": "Missing required fields"}), 400

        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        time_obj = datetime.datetime.strptime(time, '%I:%M %p').time()

        booking.date = date_obj
        booking.time = time_obj
        db.session.commit()

        return jsonify({"message": "Booking rescheduled successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to reschedule booking: {e}"}), 500
