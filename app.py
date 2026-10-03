from flask import Flask, jsonify
from db import get_db, close_db, init_db

app = Flask(__name__)
app.teardown_appcontext(close_db)
init_db()


@app.route("/api/health")
def health():
    db = get_db()
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    return jsonify({"status": "ok", "users": user_count})


if __name__ == "__main__":
    app.run(debug=True)