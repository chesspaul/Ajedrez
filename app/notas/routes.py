from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import db, Nota

notas = Blueprint("notas", __name__)

@notas.route("/notas")
@login_required
def ver_notas():
    mis_notas = Nota.query.filter_by(usuario_id=current_user.id).all()
    return render_template("notas/notas.html", notas=mis_notas)

@notas.route("/notas/nueva", methods=["GET", "POST"])
@login_required
def nueva_nota():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]

        nueva_nota = Nota(titulo=titulo, contenido=contenido, usuario_id=current_user.id)
        db.session.add(nueva_nota)
        db.session.commit()

        flash("Nota creada exitosamente.", "exito")
        return redirect(url_for("notas.ver_notas"))

    return render_template("notas/nueva_nota.html")
@notas.route("/notas/editar/<int:nota_id>", methods=["GET", "POST"])
@login_required
def editar_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)

    if nota.usuario_id != current_user.id:
        flash("No tienes permiso para editar esta nota.", "error")
        return redirect(url_for("notas.ver_notas"))

    if request.method == "POST":
        nota.titulo = request.form["titulo"]
        nota.contenido = request.form["contenido"]
        db.session.commit()

        flash("Nota actualizada exitosamente.", "exito")
        return redirect(url_for("notas.ver_notas"))
    return render_template("notas/editar_nota.html", nota=nota)

@notas.route("/notas/borrar/<int:nota_id>", methods=["POST"])
@login_required
def borrar_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)

    if nota.usuario_id != current_user.id:
        flash("No tienes permiso para borrar esta nota.", "error")
        return redirect(url_for("notas.ver_notas"))
    
    db.session.delete(nota)
    db.session.commit()
    flash("Nota borrada exitosamente.", "exito")
    return redirect(url_for("notas.ver_notas"))