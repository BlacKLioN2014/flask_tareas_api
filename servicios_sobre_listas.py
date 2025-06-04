from flask import Flask, jsonify, request

app = Flask(__name__)

tareas = [
    {"id": 1, "titulo": "Aprender Python", "completado": False},
    {"id": 2, "titulo": "Construir una API", "completado": False},
    {"id":3, "titulo": "Crear método GET", "completado":False},
    {"id":4, "titulo": "Crear método POST", "completado":False},
    {"id":5, "titulo": "Crear método PUT", "completado":False},
    {"id":6, "titulo": "Crear método DELETE", "completado":False},
]

# Método GET
@app.route("/tareas", methods=["GET"])
def obtener_tareas():
    return  jsonify(tareas)

# # método POST
@app.route("/tareas",  methods =["POST"])
def agregar_tarea():
    nueva_tarea = request.get_json()
    nueva_tarea["id"] = len(tareas) + 1
    tareas.append(nueva_tarea)
    return jsonify(nueva_tarea), 201

# Método PUT
@app.route("/tareas/<int:id>", methods=["PUT"])
def actualizar_tarea(id):
    for tarea in tareas:
        if tarea["id"] == id:
            datos = request.get_json()
            tarea["titulo"] = datos.get("titulo", tarea["titulo"])
            tarea["completado"] = datos.get("completado", tarea["completado"])
            return jsonify(tarea)
    return jsonify({"mensaje": "Tarea no encontrada"}), 404

# Método DELETE
@app.route("/tareas/<int:id>", methods=["DELETE"])
def eliminar_tarea(id):
    for tarea in tareas:
        if tarea["id"] == id:
            tareas.remove(tarea)
            return jsonify({"mensaje": "Tarea eliminada"})
    return jsonify({"mensaje": "Tarea no encontrada"}),404

# Mensaje de inicio, método get
@app.route("/")
def home():
    return jsonify({"mensaje": "¡API de tarea funcionando!"})

if __name__ == "__main__":
    app.run(debug=True)
