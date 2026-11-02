
import os
import sqlite3
from functools import wraps
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "tasks.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("register"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    status = request.args.get("status", "All")
    conn = get_db()

    if status in ("Pending", "Completed"):
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY id DESC",
            (session["user_id"], status)
        ).fetchall()
    else:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC",
            (session["user_id"],)
        ).fetchall()

    conn.close()
    return render_template(
        "dashboard.html", tasks=tasks, selected_status=status
    )


@app.route("/add", methods=["POST"])
@login_required
def add_task():
    title = request.form["title"].strip()
    description = request.form.get("description", "").strip()

    if title:
        conn = get_db()
        conn.execute(
            "INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    conn = get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    ).fetchone()

    if task is None:
        conn.close()
        return "Task not found", 404

    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form.get("description", "").strip()

        if title:
            conn.execute(
                "UPDATE tasks SET title = ?, description = ? "
                "WHERE id = ? AND user_id = ?",
                (title, description, task_id, session["user_id"])
            )
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit.html", task=task)


@app.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    conn = get_db()
    conn.execute("""
        UPDATE tasks
        SET status = CASE
            WHEN status = 'Pending' THEN 'Completed'
            ELSE 'Pending'
        END
        WHERE id = ? AND user_id = ?
    """, (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
