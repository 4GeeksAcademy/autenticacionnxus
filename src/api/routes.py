"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re
import bcrypt
from flask_cors import CORS

def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, email) is not None

api = Blueprint('api', __name__)
app = Flask(__name__)
CORS(app)

@api.route('/register', methods=['POST'])
def register_user():
    body = request.get_json()
    name = body.get('name', None)
    email = body.get('email', None)
    password = body.get('password', None)

    if name is None or email is None or password is None:
        return {'message': 'Missing arguments'}, 400

    try:
        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'User already exists'}, 400

        bpassword = bytes(password, 'utf-8')
        salt = bcrypt.gensalt(14)
        hashed_password = bcrypt.hashpw(password=bpassword, salt=salt)
        user = User(name, email, hashed_password.decode('utf-8'))

        db.session.add(user)
        db.session.commit()
        return {'message': f'User {user.email} was created'}, 201
    except Exception as e:
        return {'message': str(e)}, 500

@api.route('/token', methods=['POST'])
def create_token():
    body = request.get_json()
    email = body.get('email', None)
    password = body.get('password', None)

    if password is None or email is None:
        return {'message': f'missing parameters {email} {password}', 'authorize': False}, 400
    if not check(email):
        return {'message': 'email is not valid', 'authorize': False}, 400

    user = User.query.filter_by(email=email).one_or_none()
    if user is None:
        return {'message': 'User doesn\'t exist', 'authorize': False}, 400

    password_byte = bytes(password, 'utf-8')
    if bcrypt.checkpw(password_byte, user.password.encode('utf-8')):
        return {'token': create_access_token(identity=email), 'authorize': True}, 200

    return {'message': 'Unauthorized', 'authorize': False}, 401

@api.route('/profile/user')
@jwt_required()
def validate_user():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one_or_none()
    if user is None:
        return {'message': 'Unauthorized'}, 401
    return user.serialize(), 200

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend."
    }
    return jsonify(response_body), 200
