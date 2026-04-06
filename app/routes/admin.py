from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..decorators import login_required, role_required
from ..utils import sanitize_string, validate_username, validate_password
from ..models import get_db
import bcrypt
import datetime

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.execute("SELECT id, username, first_name, last_name FROM users WHERE role = 'professor'")
    profs = cursor.fetchall()
    cursor.execute("SELECT id, username, first_name, last_name FROM users WHERE role = 'student'")
    etudiants = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/dashboard.html",
                           classes=classes, profs=profs, etudiants=etudiants)


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def list_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        username = sanitize_string(request.form.get("username", ""))
        first_name = sanitize_string(request.form.get("first_name", ""))
        last_name = sanitize_string(request.form.get("last_name", ""))
        password = request.form.get("password", "")
        role = request.form.get("role", "student")

        valid, msg = validate_username(username)
        if not valid:
            flash(msg, "danger")
        else:
            valid, msg = validate_password(password)
            if not valid:
                flash(msg, "danger")
            else:
                hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
                cursor.execute(
                    "INSERT INTO users (username, first_name, last_name, password, role) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (username, first_name, last_name, hashed.decode("utf-8"), role)
                )
                conn.commit()
                flash(f"Compte '{username}' créé avec succès.", "success")

    cursor.execute("SELECT id, username, first_name, last_name, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/create_user.html", users=users)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_user(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        username = sanitize_string(request.form.get("username", ""))
        first_name = sanitize_string(request.form.get("first_name", ""))
        last_name = sanitize_string(request.form.get("last_name", ""))
        role = request.form.get("role")
        password = request.form.get("password", "").strip()

        valid, msg = validate_username(username)
        if not valid:
            flash(msg, "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("admin.edit_user", user_id=user_id))

        if password:
            valid, msg = validate_password(password)
            if not valid:
                flash(msg, "danger")
                cursor.close()
                conn.close()
                return redirect(url_for("admin.edit_user", user_id=user_id))
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
            cursor.execute(
                "UPDATE users SET username=%s, first_name=%s, last_name=%s, "
                "role=%s, password=%s WHERE id=%s",
                (username, first_name, last_name, role, hashed.decode("utf-8"), user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET username=%s, first_name=%s, last_name=%s, "
                "role=%s WHERE id=%s",
                (username, first_name, last_name, role, user_id)
            )
        conn.commit()
        flash("Compte mis à jour.", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("admin.list_users"))

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("admin.list_users"))

    return render_template("admin/edit_user.html", user=user)


@admin_bp.route("/classes", methods=["GET", "POST"])
@login_required
@role_required("admin")
def list_classes():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action", "create")

        if action == "create":
            name = sanitize_string(request.form.get("name", ""), max_length=100)
            if not name or len(name) < 2:
                flash("Le nom doit faire au moins 2 caractères.", "danger")
            else:
                cursor.execute("INSERT INTO classes (name) VALUES (%s)", (name,))
                conn.commit()
                flash(f"Classe '{name}' créée avec succès.", "success")

        elif action == "edit":
            class_id = request.form.get("class_id")
            name = sanitize_string(request.form.get("name", ""), max_length=100)
            if not name:
                flash("Le nom ne peut pas être vide.", "danger")
            else:
                cursor.execute("UPDATE classes SET name=%s WHERE id=%s", (name, class_id))
                conn.commit()
                flash(f"Classe renommée en '{name}'.", "success")

        elif action == "delete":
            class_id = request.form.get("class_id")
            cursor.execute("DELETE FROM classes WHERE id=%s", (class_id,))
            conn.commit()
            flash("Classe supprimée.", "success")

    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/create_class.html", classes=classes)


@admin_bp.route("/enroll", methods=["GET", "POST"])
@login_required
@role_required("admin")
def enroll_student():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action", "add_student")

        if action == "add_student":
            class_id = request.form.get("class_id")
            student_id = request.form.get("student_id")
            cursor.execute(
                "INSERT IGNORE INTO class_students (class_id, student_id) VALUES (%s, %s)",
                (class_id, student_id)
            )
            conn.commit()
            flash("Étudiant inscrit avec succès.", "success")

        elif action == "remove_student":
            class_id = request.form.get("class_id")
            student_id = request.form.get("student_id")
            cursor.execute(
                "DELETE FROM class_students WHERE class_id=%s AND student_id=%s",
                (class_id, student_id)
            )
            conn.commit()
            flash("Étudiant retiré de la classe.", "success")

        elif action == "add_professor":
            class_id = request.form.get("class_id")
            professor_id = request.form.get("professor_id")
            cursor.execute(
                "INSERT IGNORE INTO class_professors (class_id, professor_id) VALUES (%s, %s)",
                (class_id, professor_id)
            )
            conn.commit()
            flash("Professeur assigné avec succès.", "success")

        elif action == "remove_professor":
            class_id = request.form.get("class_id")
            professor_id = request.form.get("professor_id")
            cursor.execute(
                "DELETE FROM class_professors WHERE class_id=%s AND professor_id=%s",
                (class_id, professor_id)
            )
            conn.commit()
            flash("Professeur retiré de la classe.", "success")

    cursor.execute("SELECT * FROM classes ORDER BY name")
    classes = cursor.fetchall()
    cursor.execute("SELECT id, username, first_name, last_name FROM users WHERE role='student' ORDER BY username")
    students = cursor.fetchall()
    cursor.execute("SELECT id, username, first_name, last_name FROM users WHERE role='professor' ORDER BY username")
    professors = cursor.fetchall()
    cursor.execute("""
        SELECT cs.class_id, cs.student_id, u.username
        FROM class_students cs
        JOIN users u ON cs.student_id = u.id
        ORDER BY u.username
    """)
    enrollments_students = cursor.fetchall()
    cursor.execute("""
        SELECT cp.class_id, cp.professor_id, u.username
        FROM class_professors cp
        JOIN users u ON cp.professor_id = u.id
        ORDER BY u.username
    """)
    enrollments_profs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/enroll_student.html",
                           classes=classes,
                           students=students,
                           professors=professors,
                           enrollments_students=enrollments_students,
                           enrollments_profs=enrollments_profs)


@admin_bp.route("/schedule", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_schedule():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action", "create")

        if action == "create":
            class_id = request.form.get("class_id")
            subject = sanitize_string(request.form.get("subject", ""), max_length=150)
            day = request.form.get("day_of_week")
            start = request.form.get("start_time")
            end = request.form.get("end_time")
            if not all([class_id, subject, day, start, end]):
                flash("Tous les champs sont obligatoires.", "danger")
            else:
                cursor.execute(
                    "INSERT INTO schedules (class_id, title, day_of_week, start_time, end_time) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (class_id, subject, day, start, end)
                )
                conn.commit()
                flash("Créneau créé avec succès.", "success")

        elif action == "edit":
            schedule_id = request.form.get("schedule_id")
            class_id = request.form.get("class_id")
            subject = sanitize_string(request.form.get("subject", ""), max_length=150)
            day = request.form.get("day_of_week")
            start = request.form.get("start_time")
            end = request.form.get("end_time")
            if not all([schedule_id, class_id, subject, day, start, end]):
                flash("Tous les champs sont obligatoires.", "danger")
            else:
                cursor.execute(
                    "UPDATE schedules SET class_id=%s, title=%s, day_of_week=%s, "
                    "start_time=%s, end_time=%s WHERE id=%s",
                    (class_id, subject, day, start, end, schedule_id)
                )
                conn.commit()
                flash("Créneau modifié avec succès.", "success")

        elif action == "delete":
            schedule_id = request.form.get("schedule_id")
            cursor.execute("DELETE FROM schedules WHERE id=%s", (schedule_id,))
            conn.commit()
            flash("Créneau supprimé.", "success")

    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.execute("""
        SELECT s.id, s.title, s.day_of_week, s.start_time, s.end_time,
               s.class_id, c.name AS class_name
        FROM schedules s
        JOIN classes c ON s.class_id = c.id
        ORDER BY FIELD(s.day_of_week,'lundi','mardi','mercredi','jeudi','vendredi'), s.start_time
    """)
    raw_schedules = cursor.fetchall()

    def fmt_time(t):
        if isinstance(t, datetime.timedelta):
            total = int(t.total_seconds())
            return f"{total//3600:02d}:{(total % 3600)//60:02d}"
        return str(t)[:5]

    schedules = []
    for s in raw_schedules:
        s['start_str'] = fmt_time(s['start_time'])
        s['end_str'] = fmt_time(s['end_time'])
        schedules.append(s)

    cursor.close()
    conn.close()
    return render_template("admin/create_schedule.html",
                           classes=classes, schedules=schedules)


@admin_bp.route("/assign-professor", methods=["GET", "POST"])
@login_required
@role_required("admin")
def assign_professor():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        class_id = request.form.get("class_id")
        professor_id = request.form.get("professor_id")
        cursor.execute(
            "INSERT IGNORE INTO class_professors (class_id, professor_id) VALUES (%s, %s)",
            (class_id, professor_id)
        )
        conn.commit()
        flash("Professeur affecté avec succès.", "success")

    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.execute("SELECT id, username, first_name, last_name FROM users WHERE role = 'professor'")
    professors = cursor.fetchall()
    cursor.execute(
        "SELECT cp.class_id, cp.professor_id, c.name AS class_name, "
        "u.username, u.first_name, u.last_name "
        "FROM class_professors cp "
        "JOIN classes c ON cp.class_id = c.id "
        "JOIN users u ON cp.professor_id = u.id "
        "ORDER BY c.name, u.username"
    )
    assignments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/assign_professor.html",
                           classes=classes,
                           professors=professors,
                           assignments=assignments)


@admin_bp.route("/assign-professor/delete", methods=["POST"])
@login_required
@role_required("admin")
def unassign_professor():
    class_id = request.form.get("class_id")
    professor_id = request.form.get("professor_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM class_professors WHERE class_id = %s AND professor_id = %s",
        (class_id, professor_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("Affectation supprimée.", "success")
    return redirect(url_for("admin.assign_professor"))