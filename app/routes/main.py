from flask import Blueprint, render_template

from app.utils.autenticacao import login_required


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def inicio():
    return "OficialAmigurumis V2 funcionando!"


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html"
    )