from flask import Flask, render_template, request, session, Blueprint, abort, url_for, redirect, jsonify
import sqlite3

database = 'database.db'

def create_tables():
    with open('schema.sql', 'r') as f:
        sql_commands = f.read()

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.executescript(sql_commands)

    conn.commit()
    conn.close()

    print("Database schema created successfully.")

create_tables()

ep = Blueprint('endpoints', __name__)

@ep.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            abort(400)  # Bad request
        username = data['username']
        password = data['password']

        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return 'Login successful', 200 if user else abort(401)  # Unauthorized if user is not found
    except Exception as e:
        print(f"An error occurred during login: {e}")
        abort(500)  # Internal server error

@ep.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data or 'name' not in data or 'isAdmin' not in data:
            abort(400)  # Bad request
        print(data)
        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        isAdmin = data.get('isAdmin')

        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (name, username, password, isAdmin, email, bio) VALUES (?, ?, ?, ?, ?, ?)', (name, username, password, isAdmin, None, None))
        conn.commit()
        
        cursor.close()
        conn.close()

        return 'Registration successful', 200
    except Exception as e:
        print(f"An error occurred: {e}")
        abort(500)

@ep.route('/api/profile', methods=['GET'])
def get_user_data():
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        # Get JSON data
        data = request.get_json()
        if not data or 'username' not in data:
            abort(400)
        
        username = data.get('username')
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        print("User data from db for profile: ", user_data)
        cursor.close()
        conn.close()

        if user_data:
            # Return user data as JSON response
            return jsonify(user_data), 200
        else:
            return 'User not found', 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Internal Server Error', 500
    
@ep.route('/api/profile/update', methods=['POST'])
def update_profile():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'name' not in data or 'email' not in data or 'bio' not in data:
            abort(400)
        
        username = data.get('username')
        name = data.get('name')
        email = data.get('email')
        bio = data.get('bio')

        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('UPDATE users SET name = ?, email = ?, bio = ? WHERE username = ?', (name, email, bio, username))
        conn.commit()

        cursor.close()
        conn.close()

        return 'Profile updated successfully', 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Internal Server Error', 500
    
if __name__ == '__main__':
    ep.run(debug=True)