"""FocusFlow: A beginner-friendly Flask study planner app."""

from datetime import datetime, date
import sqlite3
from pathlib import Path

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------------------
# Flask app configuration
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent

# Use absolute template/static paths so the app works even if started from another cwd.
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config["SECRET_KEY"] = "focusflow-secret-key-change-me"
app.config["DATABASE"] = BASE_DIR / "focusflow.db"


# ---------------------------
# Database helper functions
# ---------------------------
def get_db():
    """Open a database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # Allows dictionary-style row access
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    """Close DB connection automatically when request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create users and tasks tables if they do not exist."""
    db = sqlite3.connect(app.config["DATABASE"])
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )

    db.commit()
    db.close()


# Create tables on startup
init_db()


# ---------------------------
# Utility helpers
# ---------------------------
def get_current_user():
    """Return currently logged-in user id (or None)."""
    return session.get("user_id")


def login_required():
    """Simple guard helper for protected routes."""
    if not get_current_user():
        flash("Please login to continue.", "warning")
        return False
    return True


# ---------------------------
# Public routes
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists. Please use another.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ---------------------------
# Protected routes
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    user_id = get_current_user()
    db = get_db()

    today_str = date.today().isoformat()

    todays_tasks = db.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = ? AND deadline = ?
        ORDER BY status, deadline ASC
        """,
        (user_id, today_str),
    ).fetchall()

    upcoming_tasks = db.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = ? AND deadline >= ?
        ORDER BY deadline ASC
        LIMIT 5
        """,
        (user_id, today_str),
    ).fetchall()

    total_tasks = db.execute(
        "SELECT COUNT(*) as count FROM tasks WHERE user_id = ?", (user_id,)
    ).fetchone()["count"]

    completed_tasks = db.execute(
        """
        SELECT COUNT(*) as count FROM tasks
        WHERE user_id = ? AND status = 'complete'
        """,
        (user_id,),
    ).fetchone()["count"]

    pending_tasks = total_tasks - completed_tasks
    progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return render_template(
        "dashboard.html",
        todays_tasks=todays_tasks,
        upcoming_tasks=upcoming_tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress_percent=progress_percent,
        today=today_str,
    )


@app.route("/tasks")
def tasks():
    if not login_required():
        return redirect(url_for("login"))

    user_id = get_current_user()
    db = get_db()

    all_tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY deadline ASC", (user_id,)
    ).fetchall()

    return render_template("tasks.html", tasks=all_tasks, today=date.today().isoformat())


@app.route("/tasks/add", methods=["POST"])
def add_task():
    if not login_required():
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()

    if not title or not subject or not deadline:
        flash("Please fill all task fields.", "danger")
        return redirect(url_for("tasks"))

    # Validate date format for beginner clarity
    try:
        datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        flash("Deadline must be in YYYY-MM-DD format.", "danger")
        return redirect(url_for("tasks"))

    db = get_db()
    db.execute(
        "INSERT INTO tasks (user_id, title, subject, deadline, status) VALUES (?, ?, ?, ?, 'pending')",
        (get_current_user(), title, subject, deadline),
    )
    db.commit()

    flash("Task added successfully!", "success")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/edit", methods=["POST"])
def edit_task(task_id):
    if not login_required():
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()

    if not title or not subject or not deadline:
        flash("All fields are required when editing.", "danger")
        return redirect(url_for("tasks"))

    db = get_db()
    db.execute(
        """
        UPDATE tasks
        SET title = ?, subject = ?, deadline = ?
        WHERE id = ? AND user_id = ?
        """,
        (title, subject, deadline, task_id, get_current_user()),
    )
    db.commit()

    flash("Task updated.", "success")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    if not login_required():
        return redirect(url_for("login"))

    db = get_db()
    task = db.execute(
        "SELECT status FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, get_current_user()),
    ).fetchone()

    if not task:
        flash("Task not found.", "danger")
        return redirect(url_for("tasks"))

    new_status = "pending" if task["status"] == "complete" else "complete"
    db.execute(
        "UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?",
        (new_status, task_id, get_current_user()),
    )
    db.commit()

    flash("Task status updated.", "info")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    if not login_required():
        return redirect(url_for("login"))

    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, get_current_user()),
    )
    db.commit()

    flash("Task deleted.", "info")
    return redirect(url_for("tasks"))


if __name__ == "__main__":
    app.run(debug=True)
