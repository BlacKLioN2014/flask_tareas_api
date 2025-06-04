from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario, Tarea
from . import db


main_bp = Blueprint('main', __name__)


@main_bp.route('/Usuario/Crear', methods=['POST'])
def registro():
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos or datos['username'] == '' or datos['password'] == '':
        abort(400, description="Faltan datos")
    if Usuario.query.filter_by(username=datos['username']).first():
        return jsonify({"msg": "Usuario ya existe"}), 409
    usuario = Usuario(
        username=datos['username'],
        password=generate_password_hash(datos['password'])
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify({"msg": "usuario registrado"}), 201


@main_bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos or datos['username'] == '' or datos['password'] == '':
        abort(400, description="Faltan datos")
    usuario = Usuario.query.filter_by(username=datos['username']).first()
    if not usuario or not check_password_hash(usuario.password, datos['password']):
        return jsonify({"msg": "credenciales inválidas"}), 401
    token = create_access_token(identity=str(usuario.id))
    return jsonify({"Usuario": usuario.username, "token": token}), 200


@main_bp.route("/Usuario/Obtener", methods=["GET"])
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
    return jsonify([user.to_dict() for user in usuarios])


@main_bp.route("/tareas", methods=["POST"])
@jwt_required()
def crear_tarea():
    usuario_id = int(get_jwt_identity())
    datos = request.get_json()
    if not datos or 'titulo' not in datos or 'completado' not in datos:
        abort(400, description="Faltan datos")
    nueva_tarea = Tarea(
        titulo=datos["titulo"],
        completado=datos.get("completado", False),
        usuario_id=usuario_id
    )
    db.session.add(nueva_tarea)
    db.session.commit()
    return jsonify(nueva_tarea.to_dict()), 201
    # return jsonify({"id": nueva_tarea.id, "titulo": nueva_tarea.titulo, "completado": nueva_tarea.completado,  "Creado":nueva_tarea.creado}), 201


@main_bp.route("/tareas", methods=["GET"])
@jwt_required()
def obtener_tareas():
    usuario_id = get_jwt_identity()
    # # Aquí podrías filtrar tareas por usuario si las tienes relacionadas
    # tareas = Tarea.query.all()
    tareas = Tarea.query.filter_by(usuario_id=usuario_id).all()
    # resultado = []
    # for tarea in tareas:
    #     resultado.append({
    #         "id": tarea.id,
    #         "titulo": tarea.titulo,
    #         "completado": tarea.completado,
    #         "Creado": tarea.creado
    #     })
    # return jsonify(resultado)
    return jsonify([tarea.to_dict() for tarea in tareas])


@main_bp.route("/tareas/<int:id>", methods=["GET"])
@jwt_required()
def obtener_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    # return jsonify({
    #     "id" : tarea.id,
    #     "titulo": tarea.titulo,
    #     "completado": tarea.completado,
    #     "creado": tarea.creado
    # })
    return jsonify(tarea.to_dict())


@main_bp.route("/tareas/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    datos = request.get_json()
    if not datos:
        abort(400, description="Datos inválidos")
    if 'titulo' in datos:
        # tarea.titulo = datos.get("titulo", tarea.titulo)
        tarea.titulo = datos['titulo']
    if 'completado' in datos:
        # tarea.completado = datos.get("completado", tarea.completado)
        tarea.completado = datos['completado']
    db.session.commit()
    # return jsonify({
    #     "id": tarea.id,
    #     "titulo": tarea.titulo,
    #     "completado": tarea.completado
    # })
    return jsonify(tarea.to_dict())


@main_bp.route("/tareas/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    # return '', 204
    return jsonify({"mensaje": f"Tarea {id} eliminada"}), 200