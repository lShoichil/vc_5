from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
import jwt
import datetime

from .config import SECRET_KEY
from flask import Blueprint, jsonify, request

from . import db
from .models import User

user_routes = Blueprint("user", __name__, template_folder="templates")


@user_routes.route("/")
def hello():
    return f"it works, go fan"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()

        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@user_routes.route("/user", methods=["GET"])
# @token_required
def get_all_users():
    users = User.query.all()

    output = []

    for user in users:
        user_data = {
            "public_id": user.public_id,
            "name": user.name,
            "password": user.password,
            "admin": user.admin,
        }
        output.append(user_data)

    return jsonify({"users": output})


# При повторном раскоментировании проверки, необходимов передать current_user
@user_routes.route("/user", methods=["POST"])
# @token_required
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data["password"], method="sha256")

    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data["name"],
        password=hashed_password,
        admin=False,
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "New user created!"})


# При повторном раскоментировании проверки, необходимов передать current_user
@user_routes.route("/user", methods=["PUT"])
@token_required
def promote_user(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "The user has been promoted!"})


@user_routes.route("/user/<public_id>", methods=["DELETE"])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "The user has been deleted!"})


@user_routes.route("/login")
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": "Basic realm=" '"Login required!"'},
        )

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": "Basic realm=" '"Login required!"'},
        )

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({"token": token})

    return make_response(
        "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
    )
