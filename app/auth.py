from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from datetime import datetime  # <== Добавь сюда!

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Маршрут регистрации нового пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        birth_date_str = request.form.get('birth_date')
        is_student = request.form.get('is_student') == '1'

        # Валидация введенных данных
        if not username or not email or not password or not last_name or not first_name:
            flash('Пожалуйста, заполните все обязательные поля.', 'warning')
            return redirect(url_for('auth.register'))
        elif password != confirm:
            flash('Пароли не совпадают. Попробуйте еще раз.', 'danger')
            return redirect(url_for('auth.register'))
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Пользователь с таким именем или email уже существует.', 'danger')
            return redirect(url_for('auth.register'))

        # Преобразуем дату рождения
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except Exception:
            flash('Ошибка в формате даты.', 'danger')
            return redirect(url_for('auth.register'))

        # Создание нового пользователя
        user = User(
            username=username,
            email=email,
            birth_date=birth_date,
            is_student=is_student,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
        )
        user.set_password(password)

        # Если студент — сохраняем баллы
        if is_student:
            user.ege_math = request.form.get('ege_math') or None
            user.ege_russian = request.form.get('ege_russian') or None
            user.ege_physics = request.form.get('ege_physics') or None

        # Если это первый пользователь, делаем его администратором
        if User.query.first() is None:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Регистрация успешно завершена!', 'success')
        return redirect(url_for('main.index'))

    # GET запрос
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Маршрут для входа пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        login_field = request.form.get('username')  # Логин или email
        password = request.form.get('password')
        user = User.query.filter_by(username=login_field).first() or User.query.filter_by(email=login_field).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.full_name or user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Неверные имя пользователя/email или пароль.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Маршрут выхода пользователя."""
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('main.index'))
