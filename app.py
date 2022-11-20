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
conexion = peewee.MySQLDatabase(user="root", password="2zN3Oqnpi7ua2y9ewkeJ", host="containers-us-west-34.railway.app", port=7210, database="railway", ssl_ca=cert_path, ssl_disabled=False)


#orm
class Materia(peewee.Model):
    cod_materia = peewee.PrimaryKeyField()
    nombre_materia = peewee.CharField(70)
    creditos = peewee.IntegerField(1)
    cupos = peewee.IntegerField(3)
    estado_materia = peewee.BooleanField()

    class Meta:
        database = conexion
        db_table = "MATERIA"

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
    nombre_usuario = peewee.CharField(40)
    password = peewee.CharField(200)

    class Meta:
        database = conexion
        db_table = "USUARIO"


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



if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")