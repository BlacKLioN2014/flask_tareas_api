
from flask import  Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    creado = db.Column(db.DateTime, default=datetime.utcnow)

    @app.route("/tareas", methods=["POST"])
    def crear_tarea():
        datos = request.get_json()
        nueva_tarea = Tarea(
            titulo=datos["titulo"],
            completado=datos.get("completado", False)
        )
        db.session.add(nueva_tarea)
        db.session.commit()
        return jsonify({"id": nueva_tarea.id, "titulo": nueva_tarea.titulo, "completado": nueva_tarea.completado}), 201

@app.route("/tareas", methods=["GET"])
def obtener_tareas():
    tareas = Tarea.query.all()
    resultado = []
    for tarea in tareas:
        resultado.append({
            "id": tarea.id,
            "titulo": tarea.titulo,
            "completado": tarea.completado
        })
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)