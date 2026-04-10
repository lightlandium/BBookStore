from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Book, Genre

admin_bp = Blueprint('admin', __name__)

# Ограничим доступ только для пользователя с id=1 (можно расширить)
def admin_required():
    if not current_user.is_authenticated or current_user.id != 1:
        flash('Доступ запрещён.', 'danger')
        return False
    return True

@admin_bp.route('/add_genre', methods=['GET', 'POST'])
@login_required
def add_genre():
    if not admin_required():
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            genre = Genre(name=name)
            db.session.add(genre)
            db.session.commit()
            flash('Жанр добавлен.', 'success')
        return redirect(url_for('admin.add_genre'))
    return render_template('admin/add_genre.html')