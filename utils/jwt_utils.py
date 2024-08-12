import jwt
from flask import current_app as app
import datetime

def generate_jwt(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration
    }, app.config['JWT_SECRET'], algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
        return decoded['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
