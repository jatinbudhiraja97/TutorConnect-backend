from flask import Blueprint, jsonify, request
from app import db
from app.models import Professor

bp = Blueprint('professor', __name__)

@bp.route('/professor_profile', methods=['GET'])
def professor_profile():
    # Professor profile logic
    ...
