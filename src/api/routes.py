"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager



api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200



@api.route('/secreto', methods=['POST', 'GET'])
#con esto lo protegemos
@jwt_required()

def handle_hello2():
    
    response_body = {
        "message": "información súper secreta"
    }

    return jsonify(response_body), 200


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@api.route("/login", methods=["POST"])
def login():

    # Obtener el email y la contraseña del cuerpo de la solicitud JSON
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    # Buscar el usuario en la base de datos por email
    user = User.query.filter_by(email=email).first()
    print(user)

    # Si el usuario no existe, devolver un mensaje de error
    if user is None:
        return jsonify({"msg": "email incorrecto"}), 401
    
    # Si la contraseña es incorrecta, devolver un mensaje de error
    if password != user.password:
        return jsonify({"msg": "contraseña incorrecta"}), 401

    # Crear un token de acceso JWT con la identidad del email del usuario
    access_token = create_access_token(identity=email)
    
    # Devolver el token de acceso en la respuesta JSON
    return jsonify(access_token=access_token)


@api.route("/signup", methods=["POST"])
def signup():
    # Obtener el cuerpo de la solicitud en formato JSON
    body = request.get_json()
    print(body)

    # Buscar un usuario en la base de datos con el email proporcionado
    user = User.query.filter_by(email=body["email"]).first()
    print(user)
    
    # Si no se encuentra un usuario con ese email, se crea uno nuevo
    if user is None:
        # Crear un nuevo objeto usuario con los datos del cuerpo de la solicitud
        user = User(email=body["email"], password=body["password"], is_active=True)
        # Añadir el nuevo usuario a la sesión de la base de datos
        db.session.add(user)
        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        # Crear una respuesta indicando que el usuario ha sido creado
        response_body = {
            "msg": "usuario creado"
        }
        return jsonify(response_body), 200
    else:
        # Si el usuario ya existe, devolver un mensaje de error
        return jsonify({"msg": "usuario ya creado con ese correo"}), 401