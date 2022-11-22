import hashlib
import peewee
from distutils.log import debug
from functools import  lru_cache
from playhouse.shortcuts import model_to_dict
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS,cross_origin
import os

app = Flask(__name__)
CORS(app)

app.secret_key = os.urandom(24)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(BASE_DIR, "DigiCertGlobalRootCA.crt.pem")
#conexion con Azure
conexion = peewee.MySQLDatabase(user="root", password="2zN3Oqnpi7ua2y9ewkeJ", host="containers-us-west-34.railway.app", port=7210, database="railway")


#orm
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
    return jsonify({'mensaje' : "Usuario logueado exitosamente!"})

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

    Materia.create(id_materia = id_materia,cod_materia = cod, nombre_materia = nom, creditos = cre, cupos = cup, estado_materia = status)

    return jsonify({'mensaje' : "Materia registrada"})

@lru_cache
def getInfoAssignature():

    cod = request.json['cod_materia']
    nom = request.json['nombre_materia']
    cre = request.json['creditos']
    cup = request.json['cupos']
    status = request.json['estado_materia']
    return cod,nom,cre,cup,status
@cross_origin
@app.route('/materia/actualizar/<codigo>', methods=["PUT"])
def actualizarMateria(codigo):
    
    nom, cre, cup, status = getInfoAssignature()

    Materia.update(nombre_materia = nom, creditos = cre, cupos = cup, estado_materia = status).where(Materia.cod_materia == codigo).execute()
    
    return jsonify({'mensaje' : "Materia actualizado"})
@cross_origin
@app.route('/materia/eliminar/<codigo>', methods=["DELETE"])
def eliminarMateria(codigo):

    Materia.delete().where(Materia.cod_materia == codigo).execute()

    return jsonify({'mensaje' : "Materia eliminada"})
    
#orm usuarios
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
    #encriptando
    enc = hashlib.sha256(password.encode())
    pass_enc = enc.hexdigest()

    Usuario.create(id_usuario = id_usuario, nombre_usuario=nombre_usuario, password = pass_enc)

    return jsonify({'mensaje' : "Usuario registrado"})
@cross_origin
@app.route("/login", methods=["POST"])
def loginUsuario():
    nombre_usuario = request.json['nombre_usuario']
    password = request.json['password']
    #encriptando
    enc = hashlib.sha256(password.encode())
    pass_enc = enc.hexdigest()

    try:
        user = Usuario.select().where(Usuario.nombre_usuario == nombre_usuario and Usuario.password == pass_enc)
        Item = [model_to_dict(item) for item in user]
    except:
        user = ""
    if(Item!=[]):
        return jsonify({'msg': "Usuario fue encontrado con exito"})
    else:
        return jsonify({'msg': "El usuario no existe "})


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

@cross_origin
@app.route("/estudiante")
def estudiante():
    return jsonify({'mensaje': "Usuario logueado exitosamente!"})

@lru_cache
@cross_origin
@app.route("/estudiante/listar")
def listarEstudiantes():
    estudiantes = Estudiante.select(Estudiante, TipoDocumento).join(TipoDocumento, attr='tip', on=(
                Estudiante.tipo_documento == TipoDocumento.id_tipo_doc)).execute()

    str = [{'id_estudiante': estudiante.id_estudiante, 'tipo_documento': estudiante.tip.nombre_tipo,
            'nombre_estudiante': estudiante.nombre_estudiante, 'apellido_estudiante': estudiante.apellido_estudiante,
            'foto': estudiante.foto, 'estado': estudiante.estado} for estudiante in estudiantes]


    return jsonify(str)

@cross_origin
@app.route("/estudiante/registrar", methods=["POST"])
def registrarEstudiante():
    id_est = request.json['cod_estudiante']
    tipo_doc, nom_est, ape_est, foto, esta = getInfoStudient()

    Estudiante.create(cod_estudiante=id_est, tipo_documento=tipo_doc, nombre_estudiante=nom_est,
                      apellido_estudiante=ape_est, foto=foto, estado=esta)

    return jsonify({'mensaje': "Estudiante registrado"})


def getInfoStudient():
    tipo_doc = request.json['tipo_documento']
    nom_est = request.json['nombre_estudiante']
    ape_est = request.json['apellido_estudiante']
    foto = request.json['foto']
    esta = request.json['estado']
    return tipo_doc, nom_est, ape_est, foto, esta

@cross_origin
@app.route('/estudiante/actualizar/<codigo>', methods=["PUT"])
def actualizarEstudiante(codigo):
    tipo_doc, nom_est, ape_est, foto, esta = getInfoStudient()

    Estudiante.update(tipo_documento=tipo_doc, nombre_estudiante=nom_est, apellido_estudiante=ape_est, foto=foto,
                      estado=esta).where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje': "Estudiante actualizado"})

@cross_origin
@app.route('/estudiante/actualizar/estado/<codigo>', methods=["PATCH"])
def actualizarEstudianteE(codigo):
    esta = request.json['estado']

    Estudiante.update(estado=esta).where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje': "Estado del Estudiante actualizado"})

@cross_origin
@app.route('/estudiante/eliminar/<codigo>', methods=["DELETE"])
def eliminarEstudiante(codigo):
    try:
        Estudiante.delete().where(Estudiante.cod_estudiante == codigo).execute()
    except:
        Estudiante.update(estado='E').where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje': "Estudiante eliminado"})

class Inscripcion(peewee.Model):
    id_estudiante =  peewee.PrimaryKeyField(11)
    id_materia = peewee.IntegerField(11)
    fecha_inscripcion = peewee.DateField()

    class Meta:
        database = conexion
        db_table = "Inscripcion"




# Inscripciones
@cross_origin
@app.route("/inscripcion")
def inscripcion():
    return jsonify({'mensaje' : "Usuario logueado exitosamente!"})

@lru_cache
@cross_origin
@app.route("/inscripcion/listar")
def listarInscripciones():

    inscripciones = Inscripcion.select(Inscripcion, Materia, Estudiante).join(Estudiante, on=(Estudiante.id_estudiante == Inscripcion.id_estudiante), attr='est').switch(Inscripcion).join(Materia, on=(Materia.cod_materia == Inscripcion.id_materia), attr='mat')
    str = [{'id_estudiante':inscripcion.id_estudiante,'nombre_estudiante': inscripcion.est.nombre_estudiante,'id_materia':inscripcion.id_materia,'nombre_materia' : inscripcion.mat.nombre_materia,'fecha_inscripcion' : inscripcion.fecha_inscripcion} for inscripcion in inscripciones]
    return jsonify(str)
@cross_origin
@app.route("/inscripcion/registrar", methods=["POST"])
def registrarInscripcion():

    id_est, id_mat, fech_ins = getInfoInscription()

    Inscripcion.create(id_estudiante = id_est, id_materia = id_mat, fecha_inscripcion = fech_ins)

    return jsonify({'mensaje' : "Inscripcion registrada"})

def getInfoInscription():
    id_est = request.json['id_estudiante']
    id_mat = request.json['id_materia']
    fech_ins = request.json['fecha_inscripcion']
    return id_est,id_mat,fech_ins
@cross_origin
@app.route('/inscripcion/eliminar/<codigo>', methods=["DELETE"])
def eliminarInscripcionE(codigo):

    Inscripcion.delete().where(Inscripcion.id_estudiante == codigo).execute()

    return jsonify({'mensaje' : "Inscripcion del estudiante a todas las materias eliminada"})
@cross_origin
@app.route('/inscripcion/eliminar/materia/<codigo>', methods=["DELETE"])
def eliminarInscripcionM(codigo):

    Inscripcion.delete().where(Inscripcion.id_materia == codigo).execute()

    return jsonify({'mensaje' : "Materia eliminada de todas las inscripciones"})
@cross_origin
@app.route('/inscripcion/eliminar/<codigo>/<codigo2>', methods=["DELETE"])
def eliminarInscripcionEM(codigo,codigo2):

    Inscripcion.delete().where(Inscripcion.id_estudiante == codigo and Inscripcion.id_materia == codigo2).execute()

    return jsonify({'mensaje' : "Una Inscripcion eliminada"})


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")