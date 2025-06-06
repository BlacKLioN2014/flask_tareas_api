from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario, Tarea
from . import db
from app.hana_service import obtener_datos_hana, login_sap
import requests


main_bp = Blueprint('main', __name__)


@main_bp.route('/Usuario/Crear', methods=['POST'])
def registro():
    """
        Crear un nuevo usuario
        ---
        tags:
          - Usuarios
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  example: "juan"
                password:
                  type: string
                  example: "123456"
        responses:
          201:
            description: Usuario registrado.
          400:
            description: Faltan datos
          409:
            description: Usuario ya existe.
        """
    ...
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos or datos['username'] == '' or datos['password'] == '':
        abort(400, description="Faltan datos")
    if Usuario.query.filter_by(username=datos['username']).first():
        return jsonify({"msg": "Usuario ya existe."}), 409
    usuario = Usuario(
        username=datos['username'],
        password=generate_password_hash(datos['password'])
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify({"msg": "Usuario registrado."}), 201


@main_bp.route('/Usuario/Login', methods=['POST'])
def login():
    """
        Iniciar sesión
    ---
    tags:
      - Usuarios
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "juan"
            password:
              type: string
              example: "123456"
    responses:
      200:
        # description: Usuario autenticado exitosamente
        schema:
          type: object
          properties:
            Usuario:
              type: string
              example: juan
            token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJh...
      400:
        description: Faltan datos
      401:
        description: Credenciales inválidas
        """
    ...
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos or datos['username'] == '' or datos['password'] == '':
        abort(400, description="Faltan datos.")
    usuario = Usuario.query.filter_by(username=datos['username']).first()
    if not usuario or not check_password_hash(usuario.password, datos['password']):
        return jsonify({"msg": "credenciales inválidas."}), 401
    token = create_access_token(identity=str(usuario.id))
    return jsonify({"Usuario": usuario.username, "token": token}), 200


@main_bp.route("/Usuario/Obtener", methods=["GET"])
@jwt_required()
def obtener_usuarios():
    """
Obtener usuarios
    ---
    tags:
      - Usuarios
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
    responses:
      200:
        description: Lista de usuarios obtenida exitosamente
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 666
              username:
                type: string
                example: Gatito
      401:
        description: "Missing Authorization Header, Token has expired. Missing Bearer type in Authorization header. Expected Authorization: Bearer <JWT>"
        """
    ...
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
    return jsonify([user.to_dict() for user in usuarios]), 200


@main_bp.route("/Tarea/Crear", methods=["POST"])
@jwt_required()
def crear_tarea():
    """
    Crear tarea
    ---
    tags:
      - Tarea
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - titulo
            - completado
          properties:
            titulo:
              type: string
              example: Realizar tarea n
            completado:
              type: boolean
              example: false
    responses:
      201:
        description: Tarea creada exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            titulo:
              type: string
              example: Realizar tarea n
            completado:
              type: boolean
              example: false
            creado:
              type: string
              format: date-time
              example: 2025-06-05 23:12:45.456789
            usuario_id:
              type: integer
              example: 1
      400:
        description: "Faltan datos."
    """
    ...
    usuario_id = int(get_jwt_identity())
    datos = request.get_json()
    if not datos or 'titulo' not in datos or 'completado' not in datos:
        abort(400, description="Faltan datos.")
    nueva_tarea = Tarea(
        titulo=datos["titulo"],
        completado=datos.get("completado", False),
        usuario_id=usuario_id
    )
    db.session.add(nueva_tarea)
    db.session.commit()
    return jsonify(nueva_tarea.to_dict()), 201
    # return jsonify({"id": nueva_tarea.id, "titulo": nueva_tarea.titulo, "completado": nueva_tarea.completado,  "Creado":nueva_tarea.creado}), 201


@main_bp.route("/Tarea/Obtener_Tareas", methods=["GET"])
@jwt_required()
def obtener_tareas():
    """
    Obtener tareas
    ---
    tags:
      - Tarea
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
    responses:
      200:
        description: Lista de tareas obtenida exitosamente
        schema:
            type: array
            items:
                type: object
                properties:
                    id:
                        type: integer
                        example: 1
                    titulo:
                        type: string
                        example: Realizar tarea n
                    completado:
                        type: boolean
                        example: false
                    creado:
                        type: string
                        format: date-time
                        example: 2025-06-05 23:12:45.456789
                    usuario_id:
                        type: integer
                        example: 1
      401:
        description: "Missing Authorization Header, Token has expired. Missing Bearer type in Authorization header. Expected Authorization: Bearer <JWT>"
    """
    ...
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


@main_bp.route("/Tarea/Obtener_Tarea", methods=["GET"])
@jwt_required()
def obtener_tarea():
    """
    Obtener tarea
    ---
    tags:
      - Tarea
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
      - name: id
        in: query
        type: integer
        required: true
        description: ID de la tarea á buscar.
        example: 1
    responses:
      200:
        description: Tarea creada exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            titulo:
              type: string
              example: Realizar tarea n
            completado:
              type: boolean
              example: false
            creado:
              type: string
              format: date-time
              example: 2025-06-05 23:12:45.456789
            usuario_id:
              type: integer
              example: 1
      404:
        description: "Dato no encontrado"
      401:
       description: "Missing Authorization Header, Token has expired. Missing Bearer type in Authorization header. Expected Authorization: Bearer <JWT>"
    """
    ...
    id = request.args.get("id", type=int)
    if id is None:
        return jsonify({"error": "Falta el parametro 'id' en query string"}),400

    usuario_id = get_jwt_identity()
    tarea = Tarea.query.filter_by(id=id, usuario_id=usuario_id).first()
    # return jsonify({
    #     "id" : tarea.id,
    #     "titulo": tarea.titulo,
    #     "completado": tarea.completado,
    #     "creado": tarea.creado
    # })
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(tarea.to_dict()), 200


@main_bp.route("/Tarea/Actualizar_Tarea", methods=["PUT"])
@jwt_required()
def actualizar_tarea():
    """
    Actualizar tarea
    ---
    tags:
      - Tarea
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
      - name: id
        in: query
        type: integer
        required: true
        description: ID de la tarea á actualizar.
        example: 1
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - titulo
            - completado
          properties:
            titulo:
              type: string
              example: Realizar tarea n
            completado:
              type: boolean
              example: false
    responses:
      200:
        description: Tarea actualizada exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            titulo:
              type: string
              example: Realizar tarea n
            completado:
              type: boolean
              example: false
            creado:
              type: string
              format: date-time
              example: 2025-06-05 23:12:45.456789
            usuario_id:
              type: integer
              example: 1
      400:
        description: "Faltan datos."
      401:
       description: "Missing Authorization Header, Token has expired. Missing Bearer type in Authorization header. Expected Authorization: Bearer <JWT>"
    """
    id = request.args.get("id", type=int)
    if id is None:
        return jsonify({"error": "Falta el parametro 'id' en query string"}),400
    usuario_id = get_jwt_identity()
    tarea = Tarea.query.filter_by(id=id, usuario_id=usuario_id).first()
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
    datos = request.get_json()
    if not datos or not isinstance(datos.get("titulo", ""), str) or not isinstance(datos.get("completado", False), bool):
        return jsonify({"error": "Datos inválidos"}), 400
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
    return jsonify(tarea.to_dict()), 200


@main_bp.route("/Tarea/Eliminar_Tarea", methods=["DELETE"])
@jwt_required()
def eliminar_tarea():
    """
    Eliminar tarea
    ---
    tags:
      - Tarea
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
      - name: id
        in: query
        type: integer
        required: true
        description: ID de la tarea á eliminar.
        example: 1
    responses:
      204:
        description: ''
      401:
       description: "Missing Authorization Header, Token has expired. Missing Bearer type in Authorization header. Expected Authorization: Bearer <JWT>"
    """
    id = request.args.get("id", type=int)
    if id is None:
        return jsonify({"error": "Falta el parametro 'id' en query string"}), 400
    usuario_id = get_jwt_identity()
    tarea = Tarea.query.filter_by(id=id, usuario_id=usuario_id).first_or_404()
    db.session.delete(tarea)
    db.session.commit()
    return '', 204


@main_bp.route('/Sap/Datos_Cliente', methods = ['GET'])
@jwt_required()
def get_datos():

    """
    Consulta información de cliente
    ---
    tags:
      - Sap
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
      - name: cardcode
        in: query
        type: integer
        required: true
        description: CardCode a buscar
        example: 1
    responses:
      200:
        description: Información de cliente en formato JSON
      400:
        description: "Falta el parámetro 'cardcode'.   o Missing 'Bearer' type in 'Authorization' header. Expected 'Authorization: Bearer <JWT>'"
      404:
        description: La información del cliente no fue encontrada
      500:
        description: Error interno del servidor
    """
    cardcode = request.args.get('cardcode')
    if not cardcode:
        return jsonify({"error": "Falta el parámetro 'cardcode'. "}), 400

    datos = obtener_datos_hana(cardcode)

    if isinstance(datos, dict) and 'error' in datos:
        return jsonify(datos), 500  # Error interno de SAP/HANA

    if not datos:
        return jsonify({"error": "La información del cliente no fue encontrada"}), 404

    return jsonify(datos), 200


@main_bp.route('/Sap/Login', methods=['POST'])
@jwt_required()
def post_login():
    """
    Realiza login con SAP B1 Service Layer
    ---
    tags:
      - Sap
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT para autenticación. Formato: Bearer <token>"
        example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ
    responses:
        200:
            description: Información de login exitosa
        401:
            description: "Missing 'Bearer' type in 'Authorization' header. Expected 'Authorization: Bearer <JWT>'"
        500:
            description: Error interno del servidor o de SAP
    """
    try:
        datos = login_sap()

        if not datos or not isinstance(datos, dict):
            return jsonify({"error": "Respuesta inválida de SAP"}), 500

        if 'SessionId' not in datos:
            return jsonify({"error": "No se recibió SessionId"}), 500

        return jsonify(datos), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error de conexión con SAP", "detalle": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Error inesperado", "detalle": str(e)}), 500