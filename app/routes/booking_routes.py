from flask import Blueprint, jsonify, request
from app import db
from app.models import Booking, Professor, Student
from app.utils.jwt_utils import decode_jwt
import datetime

bp = Blueprint('bookings', __name__)  # Define the Blueprint object

@bp.route('/book_appointment', methods=['POST'])
def book_appointment():
    token = request.headers.get('Authorization', None)

    if not token:
        return jsonify({"message": "Authorization header missing"}), 401

    try:
        token = token.split(" ")[1]
        user_id = decode_jwt(token)
    except Exception as e:
        return jsonify({"message": "Invalid token"}), 401

    professor_id = request.json.get('professor_id')
    date = request.json.get('date')
    time = request.json.get('time')

    if not professor_id or not date or not time:
        return jsonify({"message": "Missing required fields"}), 400

    # Convert date and time to appropriate formats
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    time_obj = datetime.datetime.strptime(time, '%I:%M %p').time()

    # Check if the time slot is already booked
    existing_booking = Booking.query.filter_by(professor_id=professor_id, date=date_obj, time=time_obj).first()

    if existing_booking:
        return jsonify({"message": "Time slot already booked"}), 409

    # Proceed with creating the booking
    try:
        new_booking = Booking(
            student_id=user_id,
            professor_id=professor_id,
            date=date_obj,
            time=time_obj
        )
        db.session.add(new_booking)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Failed to create booking"}), 500

    return jsonify({"message": "Booking successful"}), 201


@bp.route('/get_time_slots/<int:professor_id>', methods=['GET'])
def get_time_slots(professor_id):
    date = request.args.get('date')  # Frontend should pass the date as a query parameter

    if not date:
        return jsonify({"message": "Date is required"}), 400

    # Example time slots
    all_time_slots = [
        {"time": "09:00 AM"},
        {"time": "10:00 AM"},
        {"time": "11:00 AM"},
        {"time": "01:00 PM"},
        {"time": "02:00 PM"},
        {"time": "03:00 PM"},
    ]

    # Convert date string to a date object
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    # Query existing bookings for the professor on the given date
    booked_slots = Booking.query.filter_by(professor_id=professor_id, date=date_obj).all()
    booked_times = [booking.time.strftime("%I:%M %p") for booking in booked_slots]

    # Filter out booked time slots
    available_slots = [slot for slot in all_time_slots if slot["time"] not in booked_times]

    return jsonify(available_slots), 200


@bp.route('/get_professor_bookings', methods=['GET'])
def get_professor_bookings():
    token = request.headers.get('Authorization', None)

    if not token:
        return jsonify({"message": "Authorization header missing"}), 401

    try:
        token = token.split(" ")[1]
        user_id = decode_jwt(token)
    except Exception as e:
        return jsonify({"message": "Invalid token"}), 401

    professor = Professor.query.filter_by(user_id=user_id).first()
    if not professor:
        return jsonify({"message": "Professor profile not found"}), 404

    bookings = Booking.query.filter_by(professor_id=professor.id).all()
    bookings_list = []
    for booking in bookings:
        student = Student.query.get(booking.student_id)
        bookings_list.append({
            "student_name": student.name,
            "date": booking.date.strftime('%Y-%m-%d'),
            "time": booking.time.strftime('%I:%M %p')
        })

    return jsonify(bookings_list), 200
