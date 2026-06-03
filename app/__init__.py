from flask import Flask
from flask_login import LoginManager
from .models import db, Usuario
from .ajedrez.routes import ajedrez


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    
    app.config["SECRET_KEY"] = "clave-secreta-cambiar-en-produccion"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def cargar_usuario(user_id):
        return Usuario.query.get(int(user_id))

    from .auth.routes import auth
    from .notas.routes import notas

    app.register_blueprint(auth)
    app.register_blueprint(notas)
    app.register_blueprint(ajedrez)

    with app.app_context():
        db.create_all()

    return app