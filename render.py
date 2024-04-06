from flask import Flask, render_template, request, session, Blueprint, redirect, url_for, flash
import sqlite3
import requests

render = Blueprint('render', __name__)

@render.route('/')
def index():
    logged_in = 'username' in session
    return render_template('basewithnav.html', logged_in=logged_in)

@render.route('/login', methods=['GET', 'POST'])
def render_login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        response = requests.post('http://127.0.0.1:5000/api/login', json={'username': username, 'password': password})

        if response.status_code == 200:
            session['username'] = username
            return redirect('/')
        else:
            return 'login failed'
    else:
        return render_template('login.html')

@render.route('/register', methods=['GET', 'POST'])
def render_register_page():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        isAdmin = request.form.get('isAdmin')

        response = requests.post('http://127.0.0.1:5000/api/register', json={'username': username, 'name':name, 'password': password, 'isAdmin': isAdmin})

        if response.status_code == 200:
            return redirect('/login')
        else:
            return f'registration failed {response.status_code}'
    else:
        return render_template('register.html')

@render.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@render.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        username = session['username']
        response = requests.get('http://127.0.0.1:5000/api/profile', json={'username': username})
        
        if response.status_code == 200:
            user_data = response.json()
            name = user_data[0]

            if request.method == 'POST':
                name = request.form.get('name')
                email = request.form.get('email')
                bio = request.form.get('bio')
                
                response = requests.post('http://127.0.0.1:5000/api/profile/update', json={'username': username, 'name': name, 'email': email, 'bio': bio})

                if response.status_code == 200:
                    flash('Profile updated successfully.', 'success')
                else:
                    flash('Failed to update profile.', 'error')
                    
            return render_template('profile.html', username=username, name=name, email=user_data[1], bio=user_data[2])
        else:
            flash('Failed to fetch user data.', 'error')
            return render_template('profile.html', username=username)  
        
    flash('Please log in to view your profile.', 'error')
    return redirect('/login')



if __name__ == '__main__':
    render.run(debug=True)