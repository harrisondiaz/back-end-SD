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
class Materia(peewee.Model):
    id_materia = peewee.PrimaryKeyField()
    cod_materia = peewee.IntegerField(3)
    nombre_materia = peewee.CharField(70)
    creditos = peewee.IntegerField(1)
    cupos = peewee.IntegerField(3)
    estado_materia = peewee.BooleanField()

    class Meta:
        database = conexion
        db_table = "Materia"


# Materias
@cross_origin
@app.route("/materia")
def materia():
    return jsonify({'mensaje': "Usuario logueado exitosamente!"})


@lru_cache
@cross_origin
@app.route("/materia/listar")
def listarMaterias():
    items = Materia.select()
    items = [model_to_dict(item) for item in items]
    return jsonify(items)


@cross_origin()
@app.route("/materia/registrar", methods=["POST"])
def registrarMateria():
    id_materia = request.json['id_materia']
    cod, nom, cre, cup, status = getInfoAssignature()

    Materia.create(id_materia=id_materia, cod_materia=cod, nombre_materia=nom, creditos=cre, cupos=cup,
                   estado_materia=status)

    return jsonify({'mensaje': "Materia registrada"})


@lru_cache
def getInfoAssignature():
    cod = request.json['cod_materia']
    nom = request.json['nombre_materia']
    cre = request.json['creditos']
    cup = request.json['cupos']
    status = request.json['estado_materia']
    return cod, nom, cre, cup, status


@cross_origin()
@app.route('/materia/actualizar/<codigo>', methods=["PUT"])
def actualizarMateria(codigo):
    cod_materia = request.json['cod_materia']
    cod, nom, cre, cup, status = getInfoAssignature()

    Materia.update(cod_materia=cod, nombre_materia=nom, creditos=cre, cupos=cup, estado_materia=status).where(
        Materia.id_materia == codigo).execute()
    return jsonify({'mensaje': "Materia actualizado"})


@cross_origin
@app.route('/materia/eliminar/<codigo>', methods=["DELETE"])
def eliminarMateria(codigo):
    Materia.delete().where(Materia.id_materia == codigo).execute()

    return jsonify({'mensaje': "Materia eliminada"})




if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
