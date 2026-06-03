from flask import Blueprint, render_template
from flask_login import login_required, current_user

ajedrez = Blueprint('ajedrez', __name__)    

@ajedrez.route("/ajedrez")
@login_required
def jugar():
    return render_template("ajedrez/jugar.html", usuario=current_user)