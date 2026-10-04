import os
import sqlite3
from functools import wraps
from datetime import date
from flask import Flask, jsonify, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, close_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.teardown_appcontext(close_db)
init_db()

VALID_STATUSES = {"applied", "interview", "offer", "rejected"}

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "Nicht eingeloggt."}), 401
        g.user_id = user_id
        return view(*args, **kwargs)
    return wrapped


@app.route("/api/health")
def health():
    db = get_db()
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    return jsonify({"status": "ok", "users": user_count})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Benutzername und Passwort sind erforderlich."}), 400
    if len(password) < 8:
        return jsonify({"error": "Das Passwort muss mindestens 8 Zeichen lang sein."}), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Dieser Benutzername ist bereits vergeben."}), 409

    return jsonify({"message": "Registrierung erfolgreich."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    db = get_db()
    user = db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Benutzername oder Passwort ist falsch."}), 401

    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"message": "Login erfolgreich.", "username": user["username"]})


@app.route("/api/me")
@login_required
def me():
    db = get_db()
    user = db.execute(
        "SELECT id, username FROM users WHERE id = ?",
        (g.user_id,),
    ).fetchone()
    return jsonify({"id": user["id"], "username": user["username"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout erfolgreich."})


@app.route("/api/applications", methods=["POST"])
@login_required
def create_application():
    data = request.get_json(silent=True) or {}
    company = (data.get("company") or "").strip()
    position = (data.get("position") or "").strip()
    applied_on = (data.get("applied_on") or "").strip()
    status = data.get("status") or "applied"
    notes = (data.get("notes") or "").strip()

    if not company or not position or not applied_on:
        return jsonify({"error": "Firma, Stelle und Datum sind erforderlich."}), 400
    try:
        date.fromisoformat(applied_on)
    except ValueError:
        return jsonify({"error": "Das Datum muss im Format JJJJ-MM-TT sein."}), 400
    if status not in VALID_STATUSES:
        return jsonify({"error": "Ungültiger Status."}), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO applications (user_id, company, position, applied_on, status, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (g.user_id, company, position, applied_on, status, notes),
    )
    db.commit()
    return jsonify({"id": cursor.lastrowid, "message": "Bewerbung gespeichert."}), 201


if __name__ == "__main__":
    app.run(debug=True)