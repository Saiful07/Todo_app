from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Provide username and password', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user'] = user.username
            flash('Login successful', 'success')
            return redirect(url_for('tasks.view_tasks'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        raw_username = request.form.get('username', '')
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        username = raw_username.strip().lower()
        if not username or not password or not confirm:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))

        # Basic validation
        if len(username) < 3 or len(password) < 6:
            flash('Username must be >=3 chars and password >=6 chars', 'danger')
            return redirect(url_for('auth.register'))

        # Check duplicate
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))

        # Create user
        pw_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=pw_hash)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful — log in now', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')
