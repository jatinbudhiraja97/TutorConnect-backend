from flask import Blueprint, jsonify, request
from app import db
from app.models import Rating, Comment, User, Professor
from app.utils.jwt_utils import decode_jwt

bp = Blueprint('ratings', __name__)

@bp.route('/rate_professor', methods=['POST'])
def rate_professor():
    token = request.headers.get('Authorization', None)
    
    if not token:
        return jsonify({"message": "Authorization header missing"}), 401
    
    try:
        token = token.split(" ")[1]  # Split 'Bearer' from the token
        user_id = decode_jwt(token)
    except Exception as e:
        print(f"Token decoding failed: {e}")
        return jsonify({"message": "Invalid token"}), 401

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
        print(f"Error while submitting rating: {e}")
        return jsonify({"message": "Failed to submit rating"}), 500
