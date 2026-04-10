from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, ConfirmationForm
from app.utils import generate_confirmation_code

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash('Пользователь с таким email уже зарегистрирован.', 'danger')
            return redirect(url_for('auth.register'))
        code = generate_confirmation_code()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            confirmation_code=code,
            is_confirmed=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['confirmation_user_id'] = user.id
        flash(f'Код подтверждения: {code} (имитация)', 'info')
        return redirect(url_for('auth.confirm'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/confirm', methods=['GET', 'POST'])
def confirm():
    user_id = session.get('confirmation_user_id')
    if not user_id:
        return redirect(url_for('auth.register'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.register'))
    form = ConfirmationForm()
    if form.validate_on_submit():
        if form.code.data == user.confirmation_code:
            user.is_confirmed = True
            user.confirmation_code = None
            db.session.commit()
            login_user(user)
            session.pop('confirmation_user_id', None)
            flash('Регистрация подтверждена! Добро пожаловать.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный код подтверждения.', 'danger')
    return render_template('auth/confirm.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.is_confirmed:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Вы успешно вошли.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        flash('Неверный email, пароль или аккаунт не подтверждён.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('main.index'))