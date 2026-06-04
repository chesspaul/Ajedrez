from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, Usuario, Partida

auth = Blueprint("auth", __name__)

@auth.route("/")
def inicio ():
    return render_template("inicio.html")

@auth.route("/dashboard")
@login_required
def dashboard():
    total = Partida.query.filter_by(usuario_id=current_user.id).count()
    victorias = Partida.query.filter_by(
        usuario_id = current_user.id, resultado="blancas"
    ).count()
    derrotas = Partida.query.filter_by(
        usuario_id = current_user.id, resultado="negras"
    ).count()
    empates = Partida.query.filter_by(
        usuario_id = current_user.id, resultado="empate"
    ).count()
    return render_template("auth/dashboard.html",
        usuario = current_user,
        total = total,
        victorias = victorias,
        derrotas = derrotas,
        empates = empates
    )

@auth.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        if Usuario.query.filter_by(email=email).first():
            flash("Este email ya esta registrado", "error")
            return redirect(url_for("auth.registro"))
        
        password_hash = generate_password_hash(password)
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password_hash)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Cuenta creada. Ya puedes iniciar sesión", "exito")
        return redirect(url_for("auth.login"))
    return render_template("auth/registro.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not check_password_hash(usuario.password, password):
            flash("Email o contraseña incorrectos.", "error")
            return redirect(url_for("auth.login"))

        login_user(usuario)
        return redirect(url_for("notas.ver_notas"))

    return render_template("auth/login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.inicio"))