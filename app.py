from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-cambiar-en-produccion"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

#Modelo de usuarios
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email= db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

@login_manager.user_loader
def cargar_usuario(user_id):
    return Usuario.query.get(int(user_id))

#Crear tabla al inicio
with app.app_context():
    db.create_all()


@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("Ese email ya está registrado.", "error")
            return redirect(url_for("registro"))

        # Encriptar contraseña y guardar
        password_hash = generate_password_hash(password)
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password_hash)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password= request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not check_password_hash(usuario.password, password):
            flash("Email o contraseña incorrectos", "error")
            return redirect(url_for("login"))
        
        login_user(usuario)
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario = current_user)

# Ver todas las notas del usuario logueado
@app.route("/notas")
@login_required
def notas():
    mis_notas = Nota.query.filter_by(usuario_id=current_user.id).all()
    return render_template("notas.html", notas=mis_notas)


# Crear nota
@app.route("/notas/nueva", methods=["GET", "POST"])
@login_required
def nueva_nota():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        nota = Nota(titulo=titulo, contenido=contenido, usuario_id=current_user.id)
        db.session.add(nota)
        db.session.commit()
        flash("Nota creada.", "exito")
        return redirect(url_for("notas"))
    return render_template("nueva_nota.html")


# Editar nota
@app.route("/notas/editar/<int:nota_id>", methods=["GET", "POST"])
@login_required
def editar_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)

    # Seguridad: verificar que la nota es del usuario actual
    if nota.usuario_id != current_user.id:
        flash("No tienes permiso para editar esa nota.", "error")
        return redirect(url_for("notas"))

    if request.method == "POST":
        nota.titulo = request.form["titulo"]
        nota.contenido = request.form["contenido"]
        db.session.commit()
        flash("Nota actualizada.", "exito")
        return redirect(url_for("notas"))

    return render_template("editar_nota.html", nota=nota)


# Borrar nota
@app.route("/notas/borrar/<int:nota_id>", methods=["POST"])
@login_required
def borrar_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)

    if nota.usuario_id != current_user.id:
        flash("No tienes permiso para borrar esa nota.", "error")
        return redirect(url_for("notas"))

    db.session.delete(nota)
    db.session.commit()
    flash("Nota borrada.", "exito")
    return redirect(url_for("notas"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("inicio"))

if __name__ == "__main__": 
    app.run(debug=True)