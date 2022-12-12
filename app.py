import hashlib
import peewee
from distutils.log import debug
from functools import lru_cache
from playhouse.shortcuts import model_to_dict
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)

app.secret_key = os.urandom(24)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(BASE_DIR, "DigiCertGlobalRootCA.crt.pem")
# conexion con Azure
conexion = peewee.MySQLDatabase(user="root", password="2zN3Oqnpi7ua2y9ewkeJ", host="containers-us-west-34.railway.app",
                                port=7210, database="railway")


# orm

# orm usuarios
class Usuario(peewee.Model):
    id_usuario = peewee.PrimaryKeyField()
    nombre_usuario = peewee.CharField(30)
    password = peewee.CharField(200)

    class Meta:
        database = conexion
        db_table = "Usuario"


@cross_origin
@app.route("/registrar", methods=["POST"])
def registrarUsuario():
    id_usuario = request.json['id_usuario']
    nombre_usuario = request.json['nombre_usuario']
    password = request.json['password']
    # encriptando
    enc = hashlib.sha256(password.encode())
    pass_enc = enc.hexdigest()

    Usuario.create(id_usuario=id_usuario, nombre_usuario=nombre_usuario, password=pass_enc)

    return jsonify({'mensaje': "Usuario registrado"})


@cross_origin
@app.route("/login", methods=["POST"])
def loginUsuario():
    nombre_usuario = request.json['nombre_usuario']
    password = request.json['password']
    # encriptando
    enc = hashlib.sha256(password.encode())
    pass_enc = enc.hexdigest()

    try:
        user = Usuario.select().where(Usuario.nombre_usuario == nombre_usuario and Usuario.password == pass_enc)
        Item = [model_to_dict(item) for item in user]
    except:
        user = ""
    if (Item != []):
        return jsonify({'msg': "Usuario fue encontrado con exito"})
    else:
        return jsonify({'msg': "El usuario no existe "})




if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
