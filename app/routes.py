from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Result, Test, Option
import json
from .career_utils import (
    load_structure,
    calculate_interest_scores,
    order_scores,
    recommend_program,
    ensure_career_test,
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница. Показывает доступные тесты или приветствие."""
    tests = Test.query.filter(Test.type != 'career').all()
    career_test = ensure_career_test()
    career_id = career_test.id if career_test else None
    return render_template('index.html', tests=tests, career_test_id=career_id)

@main_bp.route('/test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(test_id):
    """Маршрут прохождения выбранного теста (как профориентационного, так и теста знаний)."""
    test = Test.query.get_or_404(test_id)
    # Ограничим доступ: обычные пользователи могут проходить оба теста,
    # здесь не требуется специальной проверки, кроме авторизации (login_required).
    if request.method == 'POST':
        # Обработка отправленных ответов на тест
        if test.type == 'knowledge':
            # Если это тест знаний (например, ввод баллов ЕГЭ)
            # Пройдем по всем вопросам и сохраним результаты в профиле пользователя
            results_parts = []
            for question in test.questions:
                field_name = f"q_{question.id}"
                answer_value = request.form.get(field_name)
                if answer_value is None or answer_value == '':
                    # Если какой-то вопрос не заполнен, предупредим и вернем форму
                    flash('Пожалуйста, заполните все поля для ввода баллов.', 'warning')
                    return render_template('test.html', test=test)
                try:
                    score = int(answer_value)
                except ValueError:
                    flash('Баллы ЕГЭ должны быть числом.', 'danger')
@@ -98,26 +108,80 @@ def take_test(test_id):
            else:
                recommendation = "Не удалось определить чёткую область интересов. Попробуйте пройти тест заново или уточнить предпочтения."
            # Финальный текст результата
            result_text = ""
            if interest_category:
                result_text += f"Основная область интересов: {interest_category}. "
            result_text += recommendation
            # Сохраняем результат в базу данных
            db.session.add(Result(user_id=current_user.id, test_id=test.id, result_text=result_text))
            db.session.commit()
            # Перенаправляем на страницу с отображением результата
            return redirect(url_for('main.result', test_id=test.id))
    # GET запрос: отобразить страницу с вопросами теста
    return render_template('test.html', test=test)

@main_bp.route('/result/<int:test_id>')
@login_required
def result(test_id):
    """Маршрут для отображения результата прохождения теста."""
    test = Test.query.get_or_404(test_id)
    # Получаем последний результат текущего пользователя для данного теста
    result = Result.query.filter_by(user_id=current_user.id, test_id=test.id).order_by(Result.timestamp.desc()).first()
    if result is None:
        flash('Результат для данного теста не найден.', 'warning')
        return redirect(url_for('main.index'))
    data = None
    if test.type == 'career':
        try:
            data = json.loads(result.result_text)
        except Exception:
            data = None
    return render_template('result.html', test=test, result=result, data=data)


@main_bp.route('/profile')
@login_required
def profile():
    """Личный профиль с результатами всех тестов."""
    user_results = Result.query.filter_by(user_id=current_user.id).order_by(Result.timestamp.desc()).all()
    career_test = Test.query.filter_by(type='career').first()
    career_id = career_test.id if career_test else None
    return render_template('profile.html', results=user_results, career_test_id=career_id)


@main_bp.route('/career_test', methods=['GET', 'POST'])
@login_required
def career_test():
    """Standalone career test based on documentation structure."""
    questions, programs = load_structure()
    career_test = ensure_career_test()
    if request.method == 'POST':
        answers = {}
        for q in questions:
            field = request.form.get(f"q_{q['id']}")
            if field is None:
                flash('Пожалуйста, ответьте на все вопросы теста.', 'warning')
                return render_template('career_test.html', questions=questions)
            answers[q['id']] = int(field)
        scores = calculate_interest_scores(questions, answers)
        ordered = order_scores(scores)
        ege_scores = {
            'math': current_user.ege_math or 0,
            'russian': current_user.ege_russian or 0,
            'physics': current_user.ege_physics or 0,
            'informatics': 0,
            'chemistry': 0,
            'social': 0,
            'language': 0,
        }
        program = recommend_program(scores, ege_scores, programs)
        data = {
            'recommended': program,
            'scores': ordered,
        }
        result_text = json.dumps(data, ensure_ascii=False)
        db.session.add(Result(user_id=current_user.id, test_id=career_test.id, result_text=result_text))
        db.session.commit()
        return redirect(url_for('main.result', test_id=career_test.id))

    return render_template('career_test.html', questions=questions)