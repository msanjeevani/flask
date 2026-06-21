from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ---------------------------
# Database Config (.env)
# ---------------------------
db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"DB connection error: {e}")
        return None

# ---------------------------
# Home
# ---------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------------------
# Dashboard
# ---------------------------
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("❌ Please login first!", "danger")
        return redirect(url_for("login"))
    return render_template('dashboard.html', user_name=session.get("user_name"))

# ---------------------------
# Register
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get("firstName").strip()
        last_name = request.form.get("lastName").strip()
        email = request.form.get("email").strip()
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not (first_name and last_name and email and username and password):
            flash("❌ Fill all fields", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email=%s OR username=%s", (email, username))
        if cursor.fetchone():
            flash("❌ Email or Username already exists", "danger")
            return redirect(url_for("register"))

        full_name = f"{first_name} {last_name}"
        created_at = datetime.now()

        cursor.execute(
            "INSERT INTO users (full_name, username, email, password, role, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
            (full_name, username, email, hashed_password, "patient", created_at)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template('register.html')

# ---------------------------
# Login
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            flash("✅ Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Invalid credentials", "danger")
            return redirect(url_for("login"))

    return render_template('login.html')

# ---------------------------
# Logout
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("✅ Logged out", "success")
    return redirect(url_for("login"))

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)