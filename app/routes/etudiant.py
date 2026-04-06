from flask import Blueprint, render_template, session
from ..decorators import login_required, role_required
from ..models import get_db

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT e.name, g.grade FROM grades g "
        "JOIN evaluations e ON g.evaluation_id = e.id "
        "WHERE g.student_id = %s",
        (session["user_id"],)
    )
    grades = cursor.fetchall()

    cursor.execute(
        "SELECT s.title, s.day_of_week, s.start_time, s.end_time "  # ← title, pas subject
        "FROM schedules s "
        "JOIN class_students cs ON s.class_id = cs.class_id "
        "WHERE cs.student_id = %s "
        "ORDER BY s.day_of_week, s.start_time",
        (session["user_id"],)
    )
    schedule = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("student/dashboard.html",
                           grades=grades, schedule=schedule)
