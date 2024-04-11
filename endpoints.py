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
        data = request.json
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

        if user:
            isadmin = user[5]
            if isadmin is None:
                isadmin = False
            else:
                isadmin = True
            return jsonify({'message': 'Login successful', 'isAdmin': isadmin}), 200
        else:
            abort(401)
    except Exception as e:
        print(f"An error occurred during login: {e}")
        abort(500)  # Internal server error


@ep.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
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

@ep.route('/api/profile', methods=['GET', 'POST'])
def get_user_data():
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        # Get JSON data
        data = request.json
        if not data or 'username' not in data:
            abort(400)
        
        username = data.get('username')
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
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
        data = request.json
        if not data or 'username' not in data or 'name' not in data or 'email' not in data or 'bio' not in data:
            abort(400)
        
        username = data.get('username')
        name = data.get('name')
        email = data.get('email')
        bio = data.get('bio')

        print("Data received:", username, name, email, bio)  # Print received data for debugging

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
    
@ep.route('/api/books', methods=['GET'])
def get_books():
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(books), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Internal Server Error', 500

@ep.route('/api/sections', methods=['GET'])
def get_sections():
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM sections')
        sections = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(sections), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Internal Server Error', 500
    
@ep.route('/api/manage/sections', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_sections():
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        data = request.json
        if not data:
            abort(400)


        if request.method == 'POST':
            if not data or 'name' not in data:
                abort(400)
            name = data.get('name')
            desc = data.get('desc')
            cursor.execute('INSERT INTO sections (name, description) VALUES (?, ?)', (name, desc))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Section added successfully', 200

        elif request.method == 'PUT':
            if not data or 'id' not in data or 'name' not in data:
                abort(400)
            id = data.get('id')
            name = data.get('name')
            desc = data.get('desc')
            if desc is None or desc == 'null' or desc == '':
                cursor.execute('UPDATE sections SET name = ? WHERE id = ?', (name, id))
            else:
                cursor.execute('UPDATE sections SET name = ?, description = ? WHERE id = ?', (name, desc, id))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Section updated successfully', 200

        elif request.method == 'DELETE':
            if not data or 'id' not in data:
                abort(400)
            id = data.get('id')
            cursor.execute('DELETE FROM sections WHERE id = ?', (id,))
            conn.commit()
            cursor.close()
            conn.close()    
            return 'Section deleted successfully', 200
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Internal Server Error', 500
    
@ep.route('/api/manage/books', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_books():
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        data = request.json
        if not data:
            abort(400)

        if request.method == 'POST':
            if not data or 'title' not in data or 'author' not in data or 'section_id' not in data or 'desc' not in data or 'copies' not in data:
                abort(400)
            title = data.get('title')
            author = data.get('author')
            section_id = data.get('section_id')
            desc = data.get('desc')
            copies = data.get('copies')
            cursor.execute('INSERT INTO books (title, author, section_id, description, copies) VALUES (?, ?, ?, ?, ?)', (title, author, section_id, desc, copies))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Book added successfully', 200

        elif request.method == 'PUT':
            if not data or 'id' not in data:
                abort(400)
            id = data.get('id')
            title = data.get('title')
            author = data.get('author')
            section_id = data.get('section_id')
            desc = data.get('desc')
            copies = data.get('copies')

            # Fetch existing book data from the database
            cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
            existing_data = cursor.fetchone()
            print('existing data: ', existing_data)
            if not existing_data:
                abort(404)  # Book not found
            # Update only the fields provided in the request
            title = existing_data[1] if title == "" else data.get('title')
            author = existing_data[2] if author == "" else data.get('author')
            section_id = existing_data[3] if section_id == "" else data.get('section_id')
            desc = existing_data[4] if desc == "" else data.get('desc')
            copies = existing_data[5] if copies == "" else data.get('copies')
            cursor.execute('UPDATE books SET title = ?, author = ?, section_id = ?, description = ?, copies = ? WHERE id = ?', (title, author, section_id, desc, copies, id))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Book updated successfully', 200


        elif request.method == 'DELETE':
            if not data or 'id' not in data:
                abort(400)
            id = data.get('id')
            cursor.execute('DELETE FROM books WHERE id = ?', (id,))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Book deleted successfully', 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Internal Server Error', 500

    
if __name__ == '__main__':
    ep.run(debug=True)