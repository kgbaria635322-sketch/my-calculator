from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "calculator.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def calculate(a, operator, b):
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b
    raise ValueError("Invalid operator.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_api():
    data = request.get_json(silent=True) or {}
    try:
        a = float(data["a"])
        b = float(data["b"])
        operator = data["operator"]
        result = calculate(a, operator, b)

        expression = f"{a:g} {operator} {b:g}"
        result_text = f"{result:g}"

        conn = sqlite3.connect(DB_NAME)
        conn.execute(
            "INSERT INTO calculations (expression, result, created_at) VALUES (?, ?, ?)",
            (expression, result_text, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "expression": expression, "result": result_text})
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/history")
def history():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, expression, result, created_at FROM calculations ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/history/clear", methods=["POST"])
def clear_history():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM calculations")
    conn.commit()
    conn.close()
    return jsonify({"success": True})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
