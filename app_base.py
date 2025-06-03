from flask_jwt_extended import jwt_manager, JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import  Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'El que siembra vientos cosecha tempestades'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


jwt = JWTManager(app)
db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable = False)
    password = db.Column(db.String(120), nullable=False)


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    creado = db.Column(db.DateTime, default=datetime.utcnow)


    def  to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'completado': self.completado
        }


    def  to_dict_usuario(self):
        return {
            'id': self.id,
            'titulo': self.username,
            'completado': self.password
        }


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": error.description
        }),400


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": error.description
        }), 404


    @app.route('/Usuario/Crear', methods= ['POST'])
    def registro():
        datos = request.get_json()
        if not datos or 'username' not in datos or 'password' not in datos:
            abort(400, description = "Faltan datos")
        if Usuario.query.filter_by(username=datos['username']).first():
            return jsonify({"msg": "Usuario ya existe"}),409
        usuario = Usuario(
            username = datos['username'],
            password = generate_password_hash(datos['password'])
        )
        db.session.add(usuario)
        db.session.commit()
        return jsonify({"msg": "usuario registrado"}),201


    @app.route("/Usuario/Obtener", methods=["GET"])
    @jwt_required()
    def obtener_usuarios():
        # usuario_id = get_jwt_identity()
        # # Aquí podrías filtrar tareas por usuario si las tienes relacionadas
        usuarios = Usuario.query.all()
        # resultado = []
        # for tarea in tareas:
        #     resultado.append({
        #         "id": tarea.id,
        #         "titulo": tarea.titulo,
        #         "completado": tarea.completado,
        #         "Creado": tarea.creado
        #     })
        # return jsonify(resultado)
        return  jsonify([usuario.to_dict_usuario() for usuario in usuarios])


    @app.route('/login', methods=['POST'])
    def login():
        datos = request.get_json()
        if not datos or 'username' not in datos or 'password' not in datos:
            abort(400, description = "Faltan datos")
        usuario = Usuario.query.filter_by(username= datos['username']).first()
        if  not usuario or not check_password_hash(usuario.password, datos['password']):
            return jsonify({"msg" : "credenciales inválidas"}), 401
        token = create_access_token(identity=usuario.id)
        return jsonify({"Usuario": usuario, "token": token}),200


    @app.route("/tareas", methods=["POST"])
    def crear_tarea():
        datos = request.get_json()
        if not datos or 'titulo' not in datos or 'completado' not in datos:
            abort(400, description = "Faltan datos")
        nueva_tarea = Tarea(
            titulo=datos["titulo"],
            completado=datos.get("completado", False)
        )
        db.session.add(nueva_tarea)
        db.session.commit()
        return  jsonify(nueva_tarea.to_dict()),201
        # return jsonify({"id": nueva_tarea.id, "titulo": nueva_tarea.titulo, "completado": nueva_tarea.completado,  "Creado":nueva_tarea.creado}), 201


    @app.route("/tareas", methods=["GET"])
    @jwt_required()
    def obtener_tareas():
        # usuario_id = get_jwt_identity()
        # # Aquí podrías filtrar tareas por usuario si las tienes relacionadas
        tareas = Tarea.query.all()
        # resultado = []
        # for tarea in tareas:
        #     resultado.append({
        #         "id": tarea.id,
        #         "titulo": tarea.titulo,
        #         "completado": tarea.completado,
        #         "Creado": tarea.creado
        #     })
        # return jsonify(resultado)
        return  jsonify([tarea.to_dict() for tarea in tareas])


    @app.route("/tareas/<int:id>", methods=["GET"])
    def obtener_tarea(id):
        tarea =Tarea.query.get_or_404(id)
        # return jsonify({
        #     "id" : tarea.id,
        #     "titulo": tarea.titulo,
        #     "completado": tarea.completado,
        #     "creado": tarea.creado
        # })
        return jsonify(tarea.to_dict())


    @app.route("/tareas/<int:id>", methods=["PUT"])
    def actualizar_tarea(id):
        tarea = Tarea.query.get_or_404(id)
        datos = request.get_json()
        if not datos:
            abort(400, description = "Datos inválidos")
        if  'titulo' in datos:
            # tarea.titulo = datos.get("titulo", tarea.titulo)
            tarea.titulo = datos['titulo']
        if  'completado' in datos:
            # tarea.completado = datos.get("completado", tarea.completado)
            tarea.completado = datos['completado']
        db.session.commit()
        # return jsonify({
        #     "id": tarea.id,
        #     "titulo": tarea.titulo,
        #     "completado": tarea.completado
        # })
        return jsonify(tarea.to_dict())


    @app.route("/tareas/<int:id>", methods=["DELETE"])
    def eliminar_tarea(id):
        tarea = Tarea.query.get_or_404(id)
        db.session.delete(tarea)
        db.session.commit()
        # return '', 204
        return jsonify({"mensaje": f"Tarea {id} eliminada"}), 200


if __name__ == "__main__":
    app.run(debug=True)