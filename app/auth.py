from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import get_user_by_username
from .utils import sanitize_string, validate_username, validate_password
import bcrypt
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = sanitize_string(request.form.get("username", ""))
        password = request.form.get("password", "")

        valid, msg = validate_username(username)
        if not valid:
            flash(msg, "danger")
            return render_template("login.html")

        if not password:
            flash("Mot de passe obligatoire.", "danger")
            return render_template("login.html")

        user = get_user_by_username(username)

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            logger.info(f"Connexion réussie — user_id={user['id']} role={user['role']}")
            return redirect(url_for("auth.dashboard"))

        logger.warning(f"Tentative échouée — username={username}")
        flash("Identifiants incorrects.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect(url_for("auth.login"))
    role = session["role"]
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "professor":
        return redirect(url_for("professor.dashboard"))
    elif role == "student":
        return redirect(url_for("student.dashboard"))
    session.clear()
    return redirect(url_for("auth.login"))