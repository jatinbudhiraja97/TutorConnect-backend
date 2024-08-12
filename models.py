from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'student' or 'professor'
    name = db.Column(db.String(150), nullable=False)
    student = db.relationship('Student', backref='user', uselist=False)
    professor = db.relationship('Professor', backref='user', uselist=False)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    subjects = db.Column(db.String(500))  # Subjects the student is interested in
    profile_picture = db.Column(db.String(500))  # URL to the profile picture
    bookings = db.relationship('Booking', backref='student', lazy=True)
    notifications = db.relationship('Notification', backref='student', lazy=True)


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


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # Rating out of 5


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(150))  # Name of the user who commented
