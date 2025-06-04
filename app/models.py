
from . import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable = False)
    password = db.Column(db.String(120), nullable=False)


    def  to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            # 'password': self.password
        }

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    creado = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('tareas', lazy= True))


    def  to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'completado': self.completado,
            'usuario_id':self.usuario_id
        }