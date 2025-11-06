from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from app import db
from app.models import Task, User

# MUST be named tasks_bp so app.__init__ imports it
tasks_bp = Blueprint('tasks', __name__)

def get_current_user():
    """Helper: return User instance for session['user'], or None."""
    username = session.get('user')
    if not username:
        return None
    return User.query.filter_by(username=username).first()

@tasks_bp.route('/')
def view_tasks():
    user = get_current_user()
    if user is None:
        flash('Login required to view tasks', 'danger')
        return redirect(url_for('auth.login'))

    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.id.asc()).all()
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/add', methods=["POST"])
def add_task():
    user = get_current_user()
    if user is None:
        flash('Login required to add tasks', 'danger')
        return redirect(url_for('auth.login'))

    title = (request.form.get('title') or '').strip()
    if not title:
        flash('Task title cannot be empty', 'danger')
        return redirect(url_for('tasks.view_tasks'))

    new_task = Task(title=title, status='Pending', user_id=user.id)
    db.session.add(new_task)
    db.session.commit()
    flash('Task added', 'success')
    return redirect(url_for('tasks.view_tasks'))

@tasks_bp.route('/toggle/<int:task_id>', methods=["POST"])
def toggle_status(task_id):
    user = get_current_user()
    if user is None:
        flash('Login required', 'danger')
        return redirect(url_for('auth.login'))

    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        flash('Task not found or access denied', 'danger')
        return redirect(url_for('tasks.view_tasks'))

    # Cycle states: Pending -> Working -> Done -> Pending
    if task.status == 'Pending':
        task.status = 'Working'
    elif task.status == 'Working':
        task.status = 'Done'
    else:
        task.status = 'Pending'

    db.session.commit()
    flash('Task status updated', 'success')
    return redirect(url_for('tasks.view_tasks'))

@tasks_bp.route('/clear', methods=["POST"])
def clear_tasks():
    user = get_current_user()
    if user is None:
        flash('Login required', 'danger')
        return redirect(url_for('auth.login'))

    # Delete only this user's tasks
    Task.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    flash('All your tasks cleared', 'info')
    return redirect(url_for('tasks.view_tasks'))

@tasks_bp.route('/delete/<int:task_id>', methods=["POST"])
def delete_task(task_id):
    """Optional: delete single task (call from UI if you add a delete button)."""
    user = get_current_user()
    if user is None:
        flash('Login required', 'danger')
        return redirect(url_for('auth.login'))

    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        flash('Task not found or access denied', 'danger')
        return redirect(url_for('tasks.view_tasks'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted', 'info')
    return redirect(url_for('tasks.view_tasks'))
