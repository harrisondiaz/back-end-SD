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



@lru_cache
def getInfoAssignature():
    cod = request.json['cod_materia']
    nom = request.json['nombre_materia']
    cre = request.json['creditos']
    cup = request.json['cupos']
    status = request.json['estado_materia']
    return cod, nom, cre, cup, status



class TipoDocumento(peewee.Model):
    id_tipo_doc = peewee.PrimaryKeyField(11)
    nombre_tipo = peewee.CharField(30)

    class Meta:
        database = conexion
        db_table = "TIPO_DOCUMENTO"


class Estudiante(peewee.Model):
    id_estudiante = peewee.PrimaryKeyField(11)
    tipo_documento = peewee.IntegerField(11)
    nombre_estudiante = peewee.CharField(30)
    apellido_estudiante = peewee.CharField(30)
    foto = peewee.CharField(150)
    estado = peewee.CharField(1)

    class Meta:
        database = conexion
        db_table = "Estudiante"



def getInfoStudient():
    tipo_doc = request.json['tipo_documento']
    nom_est = request.json['nombre_estudiante']
    ape_est = request.json['apellido_estudiante']
    foto = request.json['foto']
    esta = request.json['estado']
    return tipo_doc, nom_est, ape_est, foto, esta




class Inscripcion(peewee.Model):
    id_estudiante = peewee.PrimaryKeyField(11)
    id_materia = peewee.IntegerField(11)
    fecha_inscripcion = peewee.DateField()

    class Meta:
        database = conexion
        db_table = "Inscripcion"


# Inscripciones
@cross_origin
@app.route("/inscripcion")
def inscripcion():
    return jsonify({'mensaje': "Usuario logueado exitosamente!"})


@lru_cache
@cross_origin
@app.route("/inscripcion/listar")
def listarInscripciones():
    inscripciones = Inscripcion.select(Inscripcion, Materia, Estudiante).join(Estudiante, on=(
                Estudiante.id_estudiante == Inscripcion.id_estudiante), attr='est').switch(Inscripcion).join(Materia,
                                                                                                             on=(
                                                                                                                         Materia.cod_materia == Inscripcion.id_materia),
                                                                                                             attr='mat')
    str = [{'id_estudiante': inscripcion.id_estudiante, 'nombre_estudiante': inscripcion.est.nombre_estudiante,
            'id_materia': inscripcion.id_materia, 'nombre_materia': inscripcion.mat.nombre_materia,
            'fecha_inscripcion': inscripcion.fecha_inscripcion} for inscripcion in inscripciones]
    return jsonify(str)


@cross_origin
@app.route("/inscripcion/registrar", methods=["POST"])
def registrarInscripcion():
    id_est, id_mat, fech_ins = getInfoInscription()

    Inscripcion.create(id_estudiante=id_est, id_materia=id_mat, fecha_inscripcion=fech_ins)

    return jsonify({'mensaje': "Inscripcion registrada"})


def getInfoInscription():
    id_est = request.json['id_estudiante']
    id_mat = request.json['id_materia']
    fech_ins = request.json['fecha_inscripcion']
    return id_est, id_mat, fech_ins


@cross_origin
@app.route('/inscripcion/eliminar/<codigo>', methods=["DELETE"])
def eliminarInscripcionE(codigo):
    Inscripcion.delete().where(Inscripcion.id_estudiante == codigo).execute()

    return jsonify({'mensaje': "Inscripcion del estudiante a todas las materias eliminada"})


@cross_origin
@app.route('/inscripcion/eliminar/materia/<codigo>', methods=["DELETE"])
def eliminarInscripcionM(codigo):
    Inscripcion.delete().where(Inscripcion.id_materia == codigo).execute()

    return jsonify({'mensaje': "Materia eliminada de todas las inscripciones"})


@cross_origin
@app.route('/inscripcion/eliminar/<codigo>/<codigo2>', methods=["DELETE"])
def eliminarInscripcionEM(codigo, codigo2):
    Inscripcion.delete().where(Inscripcion.id_estudiante == codigo and Inscripcion.id_materia == codigo2).execute()

    return jsonify({'mensaje': "Una Inscripcion eliminada"})


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
