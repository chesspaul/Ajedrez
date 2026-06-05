from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, Partida
from flask_socketio import emit, join_room, leave_room
from ..import socketio

ajedrez = Blueprint('ajedrez', __name__)    
# Salas activas en memoria
# { "codigo_sala": { "blancas": user_id, "negras": user_id, "turno": "w" } }
salas = {}

@ajedrez.route("/ajedrez")
@login_required
def jugar():
    return render_template("ajedrez/jugar.html", usuario=current_user)

@ajedrez.route("/ajedrez/salas")
@login_required
def sala_espera():
    salas_disponibles = {
        codigo: sala for codigo, sala in salas.items()
        if sala["negras"] is None
    }
    return render_template("ajedrez/sala_espera.html",
                           salas=salas_disponibles,
                           usuario=current_user)

@ajedrez.route("/ajedrez/sala/<codigo>")
@login_required
def partida_online(codigo):
    if codigo not in salas:
        flash("Esa sala no existe.", "error")
        return redirect(url_for("ajedrez.sala_espera"))
    sala = salas[codigo]
    if sala["blancas"] != current_user.id and sala["negras"] != current_user.id:
        if sala["negras"] is None:
            sala["negras"] = current_user.id
            sala["nombre_negras"] = current_user.nombre
        else:
            flash("La sala está llena.", "error")
            return redirect(url_for("ajedrez.sala_espera"))
    color = "blancas" if sala["blancas"] == current_user.id else "negras"
    return render_template("ajedrez/partida_online.html",
        codigo=codigo,
        sala=sala,
        color=color,
        usuario=current_user
    )

@ajedrez.route("/ajedrez/crear_sala", methods=["POST"])
@login_required
def crear_sala():
    import random, string
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    salas[codigo]={
        "blancas": current_user.id,
        "nombre_blancas": current_user.nombre,
        "negras": None,
        "nombre_negras": None,
        "turno": "w"
    }
    return redirect(url_for("ajedrez.partida_online", codigo=codigo))

#Eventos de socketIO
@socketio.on("unirse_sala")
def unirse_sala(data):
    codigo = data["codigo"]
    join_room(codigo)
    if codigo in salas:
        sala = salas[codigo]
        emit("sala_actualizada", {
            "blancas": sala["nombre_blancas"],
            "negras": sala["nombre_negras"],
            "lista": sala["negras"] is not None
        }, room=codigo)

@socketio.on("mover_pieza")
def mover_pieza(data):
    codigo = data["codigo"]
    if codigo not in salas:
        return
    sala = salas[codigo]
    sala["turno"] = "b" if sala["turno"] == "w" else "w"
    emit("pieza_movida", {
        "from": data["from"],
        "to": data["to"],
        "promotion": data.get("promotion", "q")
    }, room=codigo, include_self=False)

@socketio.on("fin_partida")
def fin_partida(data):
    codigo = data["codigo"]
    emit("partida_terminada",{
        "resultado": data["resultado"]
    }, room=codigo)
    if codigo in salas:
        del salas[codigo]

@ajedrez.route("/ajedrez/guardar", methods=["POST"])
@login_required
def guardar_partida():
    datos = request.get_json()
    partida = Partida(
        usuario_id = current_user.id,
        modo = datos["modo"],
        dificultad = datos.get("dificultad"),
        resultado = datos["resultado"],
        movimientos = datos["movimientos"]
    )

    db.session.add(partida)
    db.session.commit()
    return jsonify({"ok": True})

@ajedrez.route("/ajedrez/historial")
@login_required
def historial():
    partidas = Partida.query.filter_by(
        usuario_id = current_user.id

    ).order_by(Partida.fecha.desc()).all()
    return render_template("ajedrez/historial.html", partidas=partidas)

@ajedrez.route("/ajedrez/partida/<int:partida_id>")
@login_required
def ver_partida(partida_id):
    partida = Partida.query.get_or_404(partida_id)
    if partida.usuario_id != current_user.id:
        flash("No tienes permiso para ver esa partida.", "error")
        return redirect(url_for("ajedrez.historial"))
    return render_template("ajedrez/ver_partida.html", partida=partida)