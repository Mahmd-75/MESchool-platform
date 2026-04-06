from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from ..decorators import login_required, role_required
from ..utils import sanitize_string, validate_grade
from ..models import get_db
import datetime

professor_bp = Blueprint("professor", __name__)


@professor_bp.route("/dashboard")
@login_required
@role_required("professor")
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT e.id, e.name, c.name AS class_name "
        "FROM evaluations e "
        "JOIN classes c ON e.class_id = c.id "
        "WHERE e.professor_id = %s",
        (session["user_id"],)
    )
    evaluations = cursor.fetchall()

    cursor.execute(
        "SELECT s.title, s.day_of_week, s.start_time, s.end_time "
        "FROM schedules s "
        "JOIN class_professors cp ON s.class_id = cp.class_id "
        "WHERE cp.professor_id = %s "
        "ORDER BY FIELD(s.day_of_week, 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi'), s.start_time",
        (session["user_id"],)
    )
    raw_schedule = cursor.fetchall()

    def fmt(t):
        if isinstance(t, datetime.timedelta):
            total = int(t.total_seconds())
            return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
        return str(t)[:5]

    schedule = []
    for s in raw_schedule:
        schedule.append({
            "title": s["title"],
            "day_of_week": s["day_of_week"],
            "start_time": fmt(s["start_time"]),
            "end_time": fmt(s["end_time"]),
        })

    cursor.close()
    conn.close()
    return render_template("professor/dashboard.html",
                           evaluations=evaluations, schedule=schedule)


@professor_bp.route("/evaluation/create", methods=["GET", "POST"])
@login_required
@role_required("professor")
def create_evaluation():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = sanitize_string(request.form.get("name", ""), max_length=150)
        class_id = request.form.get("class_id")

        if not name or len(name) < 2:
            flash("Le nom doit faire au moins 2 caractères.", "danger")
        elif not class_id:
            flash("Veuillez sélectionner une classe.", "danger")
        else:
            cursor.execute(
                "INSERT INTO evaluations (name, class_id, professor_id) VALUES (%s, %s, %s)",
                (name, class_id, session["user_id"])
            )
            conn.commit()
            flash(f"Évaluation '{name}' créée.", "success")
            cursor.close()
            conn.close()
            return redirect(url_for("professor.dashboard"))

    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("professor/create_evaluation.html", classes=classes)


@professor_bp.route("/grades/<int:evaluation_id>", methods=["GET", "POST"])
@login_required
@role_required("professor")
def manage_grades(evaluation_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        student_id = request.form.get("student_id")
        grade = request.form.get("grade")

        valid, msg = validate_grade(grade)
        if not valid:
            flash(msg, "danger")
        else:
            cursor.execute(
                "INSERT INTO grades (student_id, evaluation_id, grade) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE grade = %s",
                (student_id, evaluation_id, float(grade), float(grade))
            )
            conn.commit()
            flash("Note enregistrée.", "success")

    cursor.execute(
        "SELECT e.id, e.name, c.name AS class_name, c.id AS class_id "
        "FROM evaluations e "
        "JOIN classes c ON e.class_id = c.id "
        "WHERE e.id = %s AND e.professor_id = %s",
        (evaluation_id, session["user_id"])
    )
    evaluation = cursor.fetchone()
    if not evaluation:
        cursor.close()
        conn.close()
        abort(404)

    cursor.execute(
        "SELECT u.id, u.username, u.first_name FROM users u "
        "JOIN class_students cs ON u.id = cs.student_id "
        "WHERE cs.class_id = %s "
        "ORDER BY u.username",
        (evaluation["class_id"],)
    )
    students = cursor.fetchall()

    cursor.execute(
        "SELECT u.username, g.grade FROM grades g "
        "JOIN users u ON g.student_id = u.id "
        "WHERE g.evaluation_id = %s "
        "ORDER BY u.username",
        (evaluation_id,)
    )
    grades = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("professor/manage_grades.html",
                           evaluation=evaluation,
                           students=students,
                           grades=grades)