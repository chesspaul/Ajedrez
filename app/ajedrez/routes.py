from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, Partida

ajedrez = Blueprint('ajedrez', __name__)    

@ajedrez.route("/ajedrez")
@login_required
def jugar():
    return render_template("ajedrez/jugar.html", usuario=current_user)

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