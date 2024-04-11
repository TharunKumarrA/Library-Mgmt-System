from flask import Flask, render_template, request, session, Blueprint, redirect, url_for, flash
import sqlite3
import requests

render = Blueprint('render', __name__)

@render.route('/')
def index():
    logged_in = 'username' in session
    if logged_in and session['username'][1]:
        return redirect('/admin')
    return render_template('basewithnav.html', logged_in=logged_in)

@render.route('/login', methods=['GET', 'POST'])
def render_login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        response = requests.post('http://127.0.0.1:5000/api/login', json={'username': username, 'password': password})

        if response.status_code == 200:
            isadmin = response.json()['isAdmin']
            session['username'] = username, isadmin
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
        username = session['username'][0]
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            bio = request.form.get('bio')

            print("Data to be updated:", username, name, email, bio)
            
            response = requests.post('http://127.0.0.1:5000/api/profile/update', json={'username': username, 'name': name, 'email': email, 'bio': bio})

            if response.status_code == 200:
                flash('Profile updated successfully.', 'success')
            else:
                flash('Failed to update profile.', 'error')

        # Send a GET request to fetch user data
        response = requests.post('http://127.0.0.1:5000/api/profile', json={'username': username})

        if response.status_code == 200:
            user_data = response.json()
            print("data from API: ", user_data)
            name = user_data[1]
            email = user_data[3]
            bio = user_data[4]
            
            return render_template('profile.html', username=username, name=name, email=email, bio=bio)
        else:
            flash('Failed to fetch user data.', 'error')
            return render_template('profile.html', username=username)  
        
    flash('Please log in to view your profile.', 'error')
    return redirect('/login')

@render.route('/admin')
def admin():
    if 'username' in session and session['username'][1]:
        username = session['username'][0]
        response = requests.post('http://127.0.0.1:5000/api/profile', json={'username': username})

        if response.status_code == 200:
            user_data = response.json()
            name = user_data[0]
        return render_template('adminhome.html', name=name)
    else:
        return redirect('/login')

@render.route('/admin/manage/section', methods=['GET', 'POST'])
def manage_section():
    if 'username' in session:
        username = session['username'][0]

        if request.method == 'POST':
            method = request.form.get('_method', '').upper()  # Get the value of _method hidden field
            print("method: ", method)
            if method == 'PUT':
                # Update section
                section_id = request.form.get('edit_section_id')
                section_name = request.form.get('edit_section_name')
                section_desc = request.form.get('edit_section_desc')
                print("section_id: ", section_id, "section_name: ", section_name, "section_desc: ", section_desc)
                response = requests.put('http://127.0.0.1:5000/api/manage/sections', json={'id': section_id, 'name': section_name, 'desc': section_desc, 'method': 'PUT'}) 
                if response.status_code == 200:
                    flash('Section updated successfully.', 'success')
                else:
                    flash('Failed to update section.', 'error')
            elif method == 'DELETE':
                # Delete section
                section_id = request.form.get('delete_section_id')
                print("section_id: ", section_id)
                response = requests.delete('http://127.0.0.1:5000/api/manage/sections', json={'id': section_id, 'method': 'DELETE'})  
                if response.status_code == 200:
                    flash('Section deleted successfully.', 'success')
                else:
                    flash('Failed to delete section.', 'error')
            elif method == 'POST':
                # Create section
                section_name = request.form.get('section_name')
                section_desc = request.form.get('section_desc')
                response = requests.post('http://127.0.0.1:5000/api/manage/sections', json={'name': section_name, 'desc': section_desc, 'method': 'POST'})  
                if response.status_code == 200:
                    flash('Section created successfully.', 'success')
                else:
                    flash('Failed to create section.', 'error')

        sections = requests.get('http://127.0.0.1:5000/api/sections').json()
        print(sections)
        return render_template('managesections.html', sections=sections)
    else:
        return redirect('/login')
    
@render.route('/admin/manage/books', methods=['GET', 'POST'])
def manage_books():
    if 'username' in session:
        username = session['username'][0]

        if request.method == 'POST':
            method = request.form.get('_method', '').upper()  # Get the value of _method hidden field
            print("method: ", method)
            if method == 'PUT':
                # Update book
                book_id = request.form.get('edit_book_id')
                book_title = request.form.get('edit_book_title')
                book_author = request.form.get('edit_book_author')
                book_section = request.form.get('edit_book_section')
                book_desc = request.form.get('edit_book_desc')
                book_copies = request.form.get('edit_book_copies')

                response = requests.put('http://127.0.0.1:5000/api/manage/books', json={'id': book_id, 'title': book_title, 'author': book_author, 'section_id': book_section, 'desc': book_desc, 'copies': book_copies})

                if response.status_code == 200:
                    flash('Book updated successfully.', 'success')
                else:
                    flash('Failed to update book.', 'error')
            
            elif method == 'DELETE':
                # Delete book
                book_id = request.form.get('delete_book_id')
                print("book_id: ", book_id)

                response = requests.delete('http://127.0.0.1:5000/api/manage/books', json={'id': book_id, 'method': 'DELETE'})

                if response.status_code == 200:
                    flash('Book deleted successfully.', 'success')
                else:
                    flash('Failed to delete book.', 'error')
            
            elif method == 'POST':
                # Create book
                book_title = request.form.get('title')
                book_author = request.form.get('author')
                book_section = request.form.get('section_id')
                book_desc = request.form.get('desc')
                book_copies = request.form.get('copies')

                print("book_title: ", book_title, "book_author: ", book_author, "book_section: ", book_section, "book_desc: ", book_desc, "book_copies: ", book_copies)

                response = requests.post('http://127.0.0.1:5000/api/manage/books', json={'title': book_title, 'author': book_author, 'section_id': book_section, 'desc': book_desc, 'copies': book_copies, 'method': 'POST'})
                
                if response.status_code == 200:
                    flash('Book created successfully.', 'success')
                else:
                    flash('Failed to create book.', 'error')
        
        sections = requests.get('http://127.0.0.1:5000/api/sections').json()
        books = requests.get('http://127.0.0.1:5000/api/books').json()
        print(sections)
        print(books)
        return render_template('managebooks.html', sections=sections, books=books)
    else:
        return redirect('/login')
    
@render.route('/admin/manage/users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        username = session['username'][0]

        respose = requests.get('http://127.0.0.1:5000/api/manage/users')
        users = respose.json()
        print(users)
        return render_template('manageusers.html', users=users)
if __name__ == '__main__':
    render.run(debug=True)