from flask import Blueprint, request, jsonify
from models import Professor

search_routes = Blueprint('search_routes', __name__)

@search_routes.route('/search_professor', methods=['GET'])
def search_professor():
    query = request.args.get('query', '')
    if query:
        results = Professor.query.filter(
            (Professor.subjects.ilike(f'%{query}%')) | 
            (Professor.name.ilike(f'%{query}%'))
        ).all()
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
