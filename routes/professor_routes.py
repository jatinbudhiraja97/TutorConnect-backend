from flask import Blueprint, request, jsonify
from models import Professor, Booking, Rating, Comment
from utils.jwt_utils import decode_jwt
from extensions import db

professor_routes = Blueprint('professor_routes', __name__)

@professor_routes.route('/professor_profile', methods=['GET'])
def professor_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1]
    user_id = decode_jwt(token)
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    professor = Professor.query.filter_by(user_id=user_id).first()
    if not professor:
        return jsonify({"message": "Professor profile not found"}), 404

    return jsonify({
        "name": professor.name, 
        "department": professor.department, 
        "experience": professor.experience, 
        "subjects": professor.subjects,
        "academics": professor.academics,
        "profile_picture": professor.profile_picture
    })

@professor_routes.route('/update_professor_profile', methods=['PUT'])
def update_professor_profile():
    token = request.headers.get('Authorization', None)
    if not token:
        return jsonify({"message": "Not logged in"}), 401

    token = token.split(" ")[1]
    user_id = decode_jwt(token)

    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    professor = Professor.query.filter_by(user_id=user_id).first()
    if not professor:
        return jsonify({"message": "Professor profile not found"}), 404

    data = request.json

    professor.name = data.get('name', professor.name)
    professor.department = data.get('department', professor.department)
    professor.experience = data.get('experience', professor.experience)
    professor.subjects = data.get('subjects', professor.subjects)
    professor.academics = data.get('academics', professor.academics)
    
    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to update profile: {e}"}), 500

@professor_routes.route('/rate_professor', methods=['POST'])
def rate_professor():
    token = request.headers.get('Authorization', None)
    
    if not token:
        return jsonify({"message": "Authorization header missing"}), 401
    
    token = token.split(" ")[1]
    user_id = decode_jwt(token)

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

    try:
        rating = Rating(professor_id=professor.id, rating=rating_value)
        db.session.add(rating)
        db.session.commit()

        if comment_text:
            comment = Comment(professor_id=professor.id, comment=comment_text, user=user.name)
            db.session.add(comment)
            db.session.commit()

        return jsonify({"message": "Rating submitted successfully"}), 201

    except Exception as e:
        return jsonify({"message": f"Failed to submit rating: {e}"}), 500
    

    # Route to fetch a professor's public profile by ID
@professor_routes.route('/professor_public_profile/<int:professor_id>', methods=['GET'])
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
