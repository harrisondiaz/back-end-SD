import peewee
from distutils.log import debug
from flask import Flask, jsonify, request
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(BASE_DIR, "DigiCertGlobalRootCA.crt.pem")

#conexion con Azure
conexion = peewee.MySQLDatabase(user="root", password="2zN3Oqnpi7ua2y9ewkeJ", host="containers-us-west-34.railway.app", port=7210, database="railway", ssl_ca=cert_path, ssl_disabled=False)


class TipoDocumento(peewee.Model):
    id_tipo_doc = peewee.PrimaryKeyField(11)
    nombre_tipo = peewee.CharField(30)
    class Meta:
        database = conexion
        db_table = "TIPO_DOCUMENTO"

class Estudiante(peewee.Model):
    cod_estudiante = peewee.PrimaryKeyField(11)
    tipo_documento = peewee.IntegerField(11)
    nombre_estudiante = peewee.CharField(30)
    apellido_estudiante = peewee.CharField(30)
    foto = peewee.CharField(150)
    estado = peewee.CharField(1)
    class Meta:
        database = conexion
        db_table = "ESTUDIANTE"


@app.route("/estudiante")
def estudiante():
    return jsonify({'mensaje' : "Usuario logueado exitosamente!"})



@app.route("/estudiante/listar")
def listarEstudiantes():

    estudiantes = Estudiante.select(Estudiante, TipoDocumento).join(TipoDocumento, attr = 'tip', on=(Estudiante.tipo_documento == TipoDocumento.id_tipo_doc)).execute()

    str = [{'cod_estudiante': estudiante.cod_estudiante,'tipo_documento' : estudiante.tip.nombre_tipo,'nombre_estudiante' : estudiante.nombre_estudiante,'apellido_estudiante' : estudiante.apellido_estudiante,'foto' : estudiante.foto,'estado' : estudiante.estado} for estudiante in estudiantes]

    return jsonify(str)

@app.route("/estudiante/registrar", methods=["POST"])
def registrarEstudiante(): 
    id_est = request.json['cod_estudiante']
    tipo_doc, nom_est, ape_est,foto,esta = getInfo()

    Estudiante.create(cod_estudiante = id_est, tipo_documento = tipo_doc, nombre_estudiante = nom_est, apellido_estudiante =ape_est, foto = foto, estado = esta)

    return jsonify({'mensaje' : "Estudiante registrado"})

def getInfo():
    tipo_doc = request.json['tipo_documento']
    nom_est = request.json['nombre_estudiante']
    ape_est = request.json['apellido_estudiante']
    foto = request.json['foto']
    esta = request.json['estado']
    return tipo_doc,nom_est,ape_est,foto,esta

@app.route('/estudiante/actualizar/<codigo>', methods=["PUT"])
def actualizarEstudiante(codigo):
    
    tipo_doc, nom_est, ape_est,foto,esta = getInfo()

    Estudiante.update(tipo_documento = tipo_doc, nombre_estudiante = nom_est, apellido_estudiante =ape_est, foto = foto, estado = esta).where(Estudiante.cod_estudiante == codigo).execute()
    
    return jsonify({'mensaje' : "Estudiante actualizado"})

@app.route('/estudiante/actualizar/estado/<codigo>', methods=["PATCH"])
def actualizarEstudianteE(codigo):
    
    esta = request.json['estado']

    Estudiante.update(estado = esta).where(Estudiante.cod_estudiante == codigo).execute()
    
    return jsonify({'mensaje' : "Estado del Estudiante actualizado"})


@app.route('/estudiante/eliminar/<codigo>', methods=["DELETE"])
def eliminarEstudiante(codigo):

    try:
        Estudiante.delete().where(Estudiante.cod_estudiante == codigo).execute()
    except:
        Estudiante.update(estado = 'E').where(Estudiante.cod_estudiante == codigo).execute()

    return jsonify({'mensaje' : "Estudiante eliminado"})

if __name__ == "__main__":
    app.run(debug=True)
    

