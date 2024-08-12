import secrets

class Config:
    SECRET_KEY = secrets.token_hex(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://myuser:mypassword@localhost:5432/mydatabase'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = "your_jwt_secret_key"
