import hashlib
import peewee
from distutils.log import debug
from playhouse.shortcuts import model_to_dict
from flask import Flask, jsonify, request, redirect
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(BASE_DIR, "DigiCertGlobalRootCA.crt.pem")

#conexion con Azure
conexion = peewee.MySQLDatabase(user="root", password="2zN3Oqnpi7ua2y9ewkeJ", host="containers-us-west-34.railway.app", port=7210, database="railway")


#orm
class Materia(peewee.Model):
    cod_materia = peewee.PrimaryKeyField()
    nombre_materia = peewee.CharField(70)
    creditos = peewee.IntegerField(1)
    cupos = peewee.IntegerField(3)
    estado_materia = peewee.BooleanField()

    class Meta:
        database = conexion
        db_table = "Materia"

# Materias

@app.route("/materia")
def materia():
    return jsonify({'mensaje' : "Usuario logueado exitosamente!"})



@app.route("/materia/listar")
def listarMaterias():
    items = Materia.select()
    items = [model_to_dict(item) for item in items]

    return jsonify(items)

@app.route("/materia/registrar", methods=["POST"])
def registrarMateria(): 

    cod = request.json['cod_materia']
    nom, cre, cup, status = getInfo()

    Materia.create(cod_materia = cod, nombre_materia = nom, creditos = cre, cupos = cup, estado_materia = status)

    return jsonify({'mensaje' : "Materia registrada"})

def getInfo():
    nom = request.json['nombre_materia']
    cre = request.json['creditos']
    cup = request.json['cupos']
    status = request.json['estado_materia']
    return nom,cre,cup,status

@app.route('/materia/actualizar/<codigo>', methods=["PUT"])
def actualizarMateria(codigo):
    
    nom, cre, cup, status = getInfo()

    Materia.update(nombre_materia = nom, creditos = cre, cupos = cup, estado_materia = status).where(Materia.cod_materia == codigo).execute()
    
    return jsonify({'mensaje' : "Materia actualizado"})

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


@app.route("/estudiante")
def estudiante():
    return jsonify({'mensaje': "Usuario logueado exitosamente!"})


@app.route("/estudiante/listar")
def listarEstudiantes():
    estudiantes = Estudiante.select(Estudiante, TipoDocumento).join(TipoDocumento, attr='tip', on=(
                Estudiante.tipo_documento == TipoDocumento.id_tipo_doc)).execute()

    str = [{'id_estudiante': estudiante.id_estudiante, 'tipo_documento': estudiante.tip.nombre_tipo,
            'nombre_estudiante': estudiante.nombre_estudiante, 'apellido_estudiante': estudiante.apellido_estudiante,
            'foto': estudiante.foto, 'estado': estudiante.estado} for estudiante in estudiantes]


    return jsonify(str)


@app.route("/estudiante/registrar", methods=["POST"])
def registrarEstudiante():
    id_est = request.json['cod_estudiante']
    tipo_doc, nom_est, ape_est, foto, esta = getInfo()

    Estudiante.create(cod_estudiante=id_est, tipo_documento=tipo_doc, nombre_estudiante=nom_est,
                      apellido_estudiante=ape_est, foto=foto, estado=esta)

    return jsonify({'mensaje': "Estudiante registrado"})


def getInfo():
    tipo_doc = request.json['tipo_documento']
    nom_est = request.json['nombre_estudiante']
    ape_est = request.json['apellido_estudiante']
    foto = request.json['foto']
    esta = request.json['estado']
    return tipo_doc, nom_est, ape_est, foto, esta


@app.route('/estudiante/actualizar/<codigo>', methods=["PUT"])
def actualizarEstudiante(codigo):
    tipo_doc, nom_est, ape_est, foto, esta = getInfo()

    Estudiante.update(tipo_documento=tipo_doc, nombre_estudiante=nom_est, apellido_estudiante=ape_est, foto=foto,
                      estado=esta).where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje': "Estudiante actualizado"})


@app.route('/estudiante/actualizar/estado/<codigo>', methods=["PATCH"])
def actualizarEstudianteE(codigo):
    esta = request.json['estado']

    Estudiante.update(estado=esta).where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje': "Estado del Estudiante actualizado"})


@app.route('/estudiante/eliminar/<codigo>', methods=["DELETE"])
def eliminarEstudiante(codigo):
    try:
        Estudiante.delete().where(Estudiante.cod_estudiante == codigo).execute()
    except:
        Estudiante.update(estado='E').where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje': "Estudiante eliminado"})


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")