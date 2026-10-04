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

def parse_application(data):
    company = (data.get("company") or "").strip()
    position = (data.get("position") or "").strip()
    applied_on = (data.get("applied_on") or "").strip()
    status = data.get("status") or "applied"
    notes = (data.get("notes") or "").strip() or None

    if not company or not position or not applied_on:
        return None, "Firma, Stelle und Datum sind erforderlich."
    try:
        date.fromisoformat(applied_on)
    except ValueError:
        return None, "Das Datum muss im Format JJJJ-MM-TT sein."
    if status not in VALID_STATUSES:
        return None, "Ungültiger Status."

    values = {
        "company": company,
        "position": position,
        "applied_on": applied_on,
        "status": status,
        "notes": notes,
    }
    return values, None


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
    values, error = parse_application(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO applications (user_id, company, position, applied_on, status, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (g.user_id, values["company"], values["position"],
         values["applied_on"], values["status"], values["notes"]),
    )
    db.commit()
    return jsonify({"id": cursor.lastrowid, "message": "Bewerbung gespeichert."}), 201


@app.route("/api/applications")
@login_required
def list_applications():
    status = request.args.get("status")
    db = get_db()

    if status:
        if status not in VALID_STATUSES:
            return jsonify({"error": "Ungültiger Status."}), 400
        rows = db.execute(
            """SELECT id, company, position, applied_on, status, notes
               FROM applications
               WHERE user_id = ? AND status = ?
               ORDER BY applied_on DESC""",
            (g.user_id, status),
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT id, company, position, applied_on, status, notes
               FROM applications
               WHERE user_id = ?
               ORDER BY applied_on DESC""",
            (g.user_id,),
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.route("/api/applications/<int:app_id>", methods=["PUT"])
@login_required
def update_application(app_id):
    values, error = parse_application(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    db = get_db()
    cursor = db.execute(
        """UPDATE applications
           SET company = ?, position = ?, applied_on = ?, status = ?, notes = ?
           WHERE id = ? AND user_id = ?""",
        (values["company"], values["position"], values["applied_on"],
         values["status"], values["notes"], app_id, g.user_id),
    )
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Bewerbung nicht gefunden."}), 404
    return jsonify({"message": "Bewerbung aktualisiert."})


if __name__ == "__main__":
    app.run(debug=True)