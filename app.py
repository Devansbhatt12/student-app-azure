from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# Azure pe persistent path, local pe current dir
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "student.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS STUD_REGISTRATION (
            STU_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            STU_NAME TEXT,
            STU_CONTACT TEXT,
            STU_EMAIL TEXT,
            STU_ROLLNO TEXT,
            STU_BRANCH TEXT
        )
    """)
    conn.commit()
    return conn

@app.route("/")
def index():
    search = request.args.get("search", "")
    conn = get_db()
    if search:
        students = conn.execute(
            "SELECT * FROM STUD_REGISTRATION WHERE STU_NAME LIKE ?",
            (f"%{search}%",)
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM STUD_REGISTRATION").fetchall()
    conn.close()
    return render_template("index.html", students=students, search=search)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    email = request.form.get("email", "").strip()
    rollno = request.form.get("rollno", "").strip()
    branch = request.form.get("branch", "").strip()

    if not all([name, contact, email, rollno, branch]):
        flash("Saare fields fill karo!", "error")
        return redirect(url_for("index"))

    conn = get_db()
    conn.execute(
        "INSERT INTO STUD_REGISTRATION (STU_NAME,STU_CONTACT,STU_EMAIL,STU_ROLLNO,STU_BRANCH) VALUES (?,?,?,?,?)",
        (name, contact, email, rollno, branch)
    )
    conn.commit()
    conn.close()
    flash("Student successfully add ho gaya!", "success")
    return redirect(url_for("index"))

@app.route("/delete/<int:student_id>", methods=["POST"])
def delete(student_id):
    conn = get_db()
    conn.execute("DELETE FROM STUD_REGISTRATION WHERE STU_ID = ?", (student_id,))
    conn.commit()
    conn.close()
    flash("Student delete ho gaya!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
