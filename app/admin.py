from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Test, Question, Option, Result

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def restrict_to_admin():
    """Хук перед обработкой запросов: разрешает доступ только администратору."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if not current_user.is_admin:
        abort(403)  # Доступ запрещен для не-админов

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_index():
    """Главная страница админ-панели: список тестов и форма добавления нового теста."""
    # (Доступ контролируется хуком restrict_to_admin)
    if request.method == 'POST':
        # Создание нового теста
        title = request.form.get('title')
        description = request.form.get('description')
        test_type = request.form.get('type')
        if not title or not test_type:
            flash('Название и тип теста обязательны.', 'danger')
        else:
            new_test = Test(title=title, description=description, type=test_type)
            db.session.add(new_test)
            db.session.commit()
            flash(f'Тест "{title}" создан.', 'success')
            return redirect(url_for('admin.admin_index'))
    # Получение списка всех тестов для отображения
    tests = Test.query.all()
    return render_template('admin.html', tests=tests)

@admin_bp.route('/test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def admin_test_detail(test_id):
    """Страница управления конкретным тестом: список вопросов, добавление вопросов/вариантов."""
    test = Test.query.get_or_404(test_id)
    if request.method == 'POST':
        # Добавление нового вопроса к тесту
        question_text = request.form.get('question_text')
        if question_text:
            new_q = Question(text=question_text, test_id=test.id)
            db.session.add(new_q)
            db.session.commit()
            flash('Вопрос добавлен.', 'success')
            return redirect(url_for('admin.admin_test_detail', test_id=test.id))
    # Список вопросов этого теста для отображения
    questions = Question.query.filter_by(test_id=test.id).all()
    return render_template('admin.html', test=test, questions=questions)

@admin_bp.route('/question/<int:question_id>/add_option', methods=['POST'])
@login_required
def admin_add_option(question_id):
    """Обработка добавления варианта ответа к вопросу."""
    question = Question.query.get_or_404(question_id)
    option_text = request.form.get('option_text')
    score = request.form.get('score')
    category = request.form.get('category')
    if option_text:
        try:
            score_val = int(score) if score else 0
        except ValueError:
            score_val = 0
        new_option = Option(text=option_text, score=score_val, category=category, question_id=question.id)
        db.session.add(new_option)
        db.session.commit()
        flash('Вариант ответа добавлен.', 'success')
    # После добавления варианта возвращаемся на страницу управления тестом
    return redirect(url_for('admin.admin_test_detail', test_id=question.test_id))

@admin_bp.route('/test/<int:test_id>/delete')
@login_required
def admin_delete_test(test_id):
    """Удаление теста вместе со всеми вопросами и результатами."""
    test = Test.query.get_or_404(test_id)
    db.session.delete(test)
    db.session.commit()
    flash(f'Тест "{test.title}" удалён.', 'info')
    return redirect(url_for('admin.admin_index'))

@admin_bp.route('/question/<int:question_id>/delete')
@login_required
def admin_delete_question(question_id):
    """Удаление вопроса (и связанных с ним вариантов ответов)."""
    question = Question.query.get_or_404(question_id)
    test_id = question.test_id
    db.session.delete(question)
    db.session.commit()
    flash('Вопрос удалён.', 'info')
    return redirect(url_for('admin.admin_test_detail', test_id=test_id))

@admin_bp.route('/option/<int:option_id>/delete')
@login_required
def admin_delete_option(option_id):
    """Удаление варианта ответа."""
    option = Option.query.get_or_404(option_id)
    test_id = option.question.test_id
    db.session.delete(option)
    db.session.commit()
    flash('Вариант ответа удалён.', 'info')
    return redirect(url_for('admin.admin_test_detail', test_id=test_id))
