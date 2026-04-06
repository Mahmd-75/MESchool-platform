import mysql.connector
from flask import current_app
import bcrypt

def get_db():
    conn = mysql.connector.connect(
        host=current_app.config["MYSQL_HOST"],
        port=current_app.config["MYSQL_PORT"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DB"]
    )
    return conn

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_all_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, first_name, last_name, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def update_user(user_id, username, first_name, last_name, new_password=None):
    conn = get_db()
    cursor = conn.cursor()

    if new_password:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            UPDATE users 
            SET username = %s, first_name = %s, last_name = %s, password = %s
            WHERE id = %s
        """, (username, first_name, last_name, hashed.decode('utf-8'), user_id))
    else:
        cursor.execute("""
            UPDATE users 
            SET username = %s, first_name = %s, last_name = %s
            WHERE id = %s
        """, (username, first_name, last_name, user_id))

    conn.commit()  # ← CRUCIAL
    cursor.close()
    conn.close()