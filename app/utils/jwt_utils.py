import jwt
import datetime
from flask import current_app

JWT_SECRET = "your_jwt_secret_key"

def generate_jwt(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, JWT_SECRET, algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return decoded['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
