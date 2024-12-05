from flask import Flask, jsonify, request, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import jwt
import datetime

app = Flask(__name__)

# Generate a secure secret key for session management
app.secret_key = secrets.token_hex(24)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost:5432/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure CORS with support for credentials
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

# JWT Secret
JWT_SECRET = "your_jwt_secret_key"  # Ensure this is consistent

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'student' or 'professor'
    name = db.Column(db.String(150), nullable=False)  # Add this line to include the name field
    student = db.relationship('Student', backref='user', uselist=False)
    professor = db.relationship('Professor', backref='user', uselist=False)


# Student Model
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    subjects = db.Column(db.String(500))  # Subjects the student is interested in
    profile_picture = db.Column(db.String(500))  # URL to the profile picture
    bookings = db.relationship('Booking', backref='student', lazy=True)
    notifications = db.relationship('Notification', backref='student', lazy=True)

# Professor Model
class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(150))
    experience = db.Column(db.Integer)  # Years of experience
    subjects = db.Column(db.String(500))  # Subjects the professor teaches
    academics = db.Column(db.Text)  # Academic achievements
    profile_picture = db.Column(db.String(500))  # URL to the profile picture
    ratings = db.relationship('Rating', backref='professor', lazy=True)
    comments = db.relationship('Comment', backref='professor', lazy=True)
    bookings = db.relationship('Booking', backref='professor', lazy=True)

# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('professor_id', 'date', 'time', name='unique_booking_constraint'),
    )


# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)

# Rating Model
class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # Rating out of 5

# Comment Model
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(150))  # Name of the user who commented

# Automatically create the tables if they don't exist
with app.app_context():
    db.create_all()

# Basic route to test the API
@app.route('/')
def home():
    return "Welcome to the Smart Tutor Backend!"

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def generate_jwt(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration
    }, JWT_SECRET, algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return decoded['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Route to create a new user and related profile
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')  # Ensure name is captured from the request
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


# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], role=data['role']).first()

    if user and check_password_hash(user.password, data['password']):
        token = generate_jwt(user.id)
        response = jsonify({"message": "Login successful", "token": token})
        response.set_cookie('token', token, httponly=True)
        return response
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@app.route('/student_profile', methods=['GET'])
def student_profile():
    print("Accessed /student_profile route")
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        print("Authorization header missing")
        return jsonify({"message": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1] if auth_header else None
    user_id = decode_jwt(token)
    print("Decoded user_id from JWT:", user_id)
    
    if not user_id:
        print("User not logged in")
        return jsonify({"message": "Not logged in"}), 401

    student = Student.query.filter_by(user_id=user_id).first()
    print("Queried student:", student)
    
    if not student:
        print("Student profile not found")
        return jsonify({"message": "Student profile not found"}), 404

    return jsonify({
        "name": student.name,
        "profile_picture": None,
        "subjects": student.subjects
    })

# Professor Profile Route
@app.route('/professor_profile', methods=['GET'])
def professor_profile():
    print("Accessed /professor_profile route")  # Debugging

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        print("Authorization header missing")  # Debugging
        return jsonify({"message": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1] if auth_header else None
    user_id = decode_jwt(token)
    if not user_id:
        print("Invalid token or user ID could not be decoded")  # Debugging
        return jsonify({"message": "Not logged in"}), 401

    professor = Professor.query.filter_by(user_id=user_id).first()
    if not professor:
        print(f"No professor found with user_id: {user_id}")  # Debugging
        return jsonify({"message": "Professor profile not found"}), 404

    print(f"Professor profile found: {professor.name}")  # Debugging
    return jsonify({
        "name": professor.name, 
        "department": professor.department, 
        "experience": professor.experience, 
        "subjects": professor.subjects,
        "academics": professor.academics,
        "profile_picture": professor.profile_picture
    })

# Route to fetch all professors
@app.route('/get_all_professors', methods=['GET'])
def get_all_professors():
    token = request.headers.get('Authorization', None)
    
    if not token:
        return jsonify({"message": "Authorization header missing"}), 401
    
    try:
        token = token.split(" ")[1]  # Split 'Bearer' from the token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded['user_id']
    except Exception as e:
        print("Token decoding failed:", e)
        return jsonify({"message": "Invalid token"}), 401
    
    professors = Professor.query.all()
    result = []
    for professor in professors:
        ratings = [r.rating for r in professor.ratings]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        result.append({
            "id": professor.id,
            "name": professor.name,
            "department": professor.department,
            "subjects": professor.subjects,
            "average_rating": avg_rating
        })
    return jsonify(result), 200

# Route to fetch a professor's public profile by ID
@app.route('/professor_public_profile/<int:professor_id>', methods=['GET'])
def professor_public_profile(professor_id):
    professor = Professor.query.get(professor_id)
    if professor:
        ratings = [r.rating for r in professor.ratings]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        comments = [{"user": c.user, "comment": c.comment} for c in professor.comments]
        return jsonify({
            "id": professor.id,
            "name": professor.name,
            "department": professor.department,
            "experience": professor.experience,
            "subjects": professor.subjects,
            "academics": professor.academics,
            "profile_picture": professor.profile_picture,
            "average_rating": avg_rating,
            "rating_count": len(ratings),
            "comments": comments
        })
    return jsonify({"message": "Professor not found"}), 404

# Route to search professors by subject
@app.route('/search_professor', methods=['GET'])
def search_professor():
    query = request.args.get('query', '')
    
    if query:
        results = Professor.query.filter(
            (Professor.subjects.ilike(f'%{query}%')) |
            (Professor.name.ilike(f'%{query}%'))
        ).all()  # Fixed extra parenthesis here
    else:
        results = Professor.query.all()

    professors = [{
        "id": prof.id,
        "name": prof.name,
        "department": prof.department,
        "subjects": prof.subjects,
        "average_rating": sum([r.rating for r in prof.ratings]) / len(prof.ratings) if prof.ratings else 0
    } for prof in results]
    
    return jsonify(professors), 200


# Route to list professors
@app.route('/list_professors', methods=['GET'])
def list_professors():
    professors = Professor.query.all()
    professor_list = [{"id": prof.id, "name": prof.name, "department": prof.department} for prof in professors]
    return jsonify(professor_list)

# Route to get available time slots for a professor
@app.route('/get_time_slots/<int:professor_id>', methods=['GET'])
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


@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    print("book_appointment method accessed")

    token = request.headers.get('Authorization', None)

    if not token:
        print("Authorization header missing")
        return jsonify({"message": "Authorization header missing"}), 401

    try:
        token = token.split(" ")[1]
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        student_id = decoded.get('user_id')
        print(f"Decoded token successfully: Student ID: {student_id}")
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        print("Invalid token")
        return jsonify({"message": "Invalid token"}), 401

    professor_id = request.json.get('professor_id')
    date = request.json.get('date')
    time = request.json.get('time')

    print(f"Professor ID: {professor_id}")
    print(f"Date: {date}")
    print(f"Time: {time}")

    if not professor_id or not date or not time:
        print("Missing required fields")
        return jsonify({"message": "Missing required fields"}), 400

    # Convert date and time to appropriate formats
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    time_obj = datetime.datetime.strptime(time, '%I:%M %p').time()

    # Check if the time slot is already booked
    existing_booking = Booking.query.filter_by(professor_id=professor_id, date=date_obj, time=time_obj).first()

    if existing_booking:
        print("Time slot already booked")
        return jsonify({"message": "Time slot already booked"}), 409

    # Proceed with creating the booking
    try:
        new_booking = Booking(
            student_id=student_id,
            professor_id=professor_id,
            date=date_obj,
            time=time_obj
        )
        db.session.add(new_booking)
        db.session.commit()
        print("Booking created successfully")
    except Exception as e:
        print(f"Error while creating booking: {e}")
        return jsonify({"message": "Failed to create booking"}), 500

    return jsonify({"message": "Booking successful"}), 201




# Route to get booking history
@app.route('/student_history', methods=['GET'])
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

# Route to get upcoming notifications
@app.route('/student_notifications', methods=['GET'])
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

@app.route('/update_professor_profile', methods=['PUT'])
def update_professor_profile():
    print("Accessing update_professor_profile route")  # Debugging

    token = request.headers.get('Authorization', None)
    if not token:
        print("Authorization header missing")  # Debugging
        return jsonify({"message": "Not logged in"}), 401

    try:
        token = token.split(" ")[1]  # Split 'Bearer' from the token
        user_id = decode_jwt(token)
    except Exception as e:
        print(f"Token decoding failed: {e}")  # Debugging
        return jsonify({"message": "Invalid token"}), 401

    print(f"User ID decoded from token: {user_id}")  # Debugging

    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    professor = Professor.query.filter_by(user_id=user_id).first()
    if not professor:
        print("Professor profile not found")  # Debugging
        return jsonify({"message": "Professor profile not found"}), 404

    data = request.json
    print(f"Received data for update: {data}")  # Debugging

    professor.name = data.get('name', professor.name)
    professor.department = data.get('department', professor.department)
    professor.experience = data.get('experience', professor.experience)
    professor.subjects = data.get('subjects', professor.subjects)
    professor.academics = data.get('academics', professor.academics)
    
    try:
        db.session.commit()
        print("Profile updated successfully")  # Debugging
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        print(f"Error while updating profile: {e}")  # Debugging
        return jsonify({"message": "Failed to update profile"}), 500

    

# Route to get professor's bookings@app.route('/professor_bookings', methods=['GET'])
@app.route('/get_professor_bookings', methods=['GET'])
def get_professor_bookings():
    print("Accessing get_professor_bookings route")  # Debugging

    token = request.headers.get('Authorization', None)
    if not token:
        print("Authorization header missing")  # Debugging
        return jsonify({"message": "Not logged in"}), 401

    try:
        token = token.split(" ")[1]  # Split 'Bearer' from the token
        user_id = decode_jwt(token)
    except Exception as e:
        print(f"Token decoding failed: {e}")  # Debugging
        return jsonify({"message": "Invalid token"}), 401

    print(f"User ID decoded from token: {user_id}")  # Debugging

    professor = Professor.query.filter_by(user_id=user_id).first()
    if not professor:
        print("Professor profile not found")  # Debugging
        return jsonify({"message": "Professor profile not found"}), 404

    bookings = Booking.query.filter_by(professor_id=professor.id).all()
    bookings_list = []
    for booking in bookings:
        student = Student.query.get(booking.student_id)
        if student:  # Check if student exists
            bookings_list.append({
                "student_name": student.name,
                "date": booking.date.strftime('%Y-%m-%d'),
                "time": booking.time.strftime('%I:%M %p')
            })
        else:
            print(f"Warning: Student with ID {booking.student_id} not found for booking ID {booking.id}.")  # Debugging

    print(f"Returning {len(bookings_list)} bookings for professor {professor.name}")  # Debugging
    return jsonify(bookings_list), 200


@app.route('/rate_professor', methods=['POST'])
def rate_professor():
    token = request.headers.get('Authorization', None)
    
    if not token:
        return jsonify({"message": "Authorization header missing"}), 401
    
    try:
        token = token.split(" ")[1]  # Split 'Bearer' from the token
        user_id = decode_jwt(token)
    except Exception as e:
        print(f"Token decoding failed: {e}")  # Debugging
        return jsonify({"message": "Invalid token"}), 401

    # Fetch the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.json
    professor_id = data.get('professorId')
    rating_value = data.get('rating')
    comment_text = data.get('comment')

    professor = Professor.query.get(professor_id)
    if not professor:
        return jsonify({"message": "Professor not found"}), 404

    # Create the rating
    try:
        rating = Rating(professor_id=professor.id, rating=rating_value)
        db.session.add(rating)
        db.session.commit()

        # Create the comment
        if comment_text:
            comment = Comment(professor_id=professor.id, comment=comment_text, user=user.name)
            db.session.add(comment)
            db.session.commit()

        return jsonify({"message": "Rating submitted successfully"}), 201

    except Exception as e:
        print(f"Error while submitting rating: {e}")
        return jsonify({"message": "Failed to submit rating"}), 500

if __name__ == '__main__':
    app.run(debug=True)
