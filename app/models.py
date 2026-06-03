from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import func

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email= db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    notas = db.relationship("Nota", backref="autor", lazy=True)
    partidas = db.relationship("Partida", backref="jugador", lazy=True)
class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

class Partida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    modo = db.Column(db.String(20), nullable=False)        # '2jugadores' o 'vs_ia'
    dificultad = db.Column(db.Integer, nullable=True) 
    resultado = db.Column(db.String(20), nullable=False)
    movimientos = db.Column(db.Text, nullable=False) #Historial de movimientos en formato JSON o similar
    fecha = db.Column(db.DateTime, default = func.now())
