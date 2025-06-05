from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Result, Test, Question, Option

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница. Показывает доступные тесты или приветствие."""
    tests = Test.query.all()
    career_test = Test.query.filter_by(type='career').first()
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
                    return render_template('test.html', test=test)
                # Сохраняем соответствующие баллы в профиль пользователя (если распознана предметная область)
                q_text_lower = question.text.lower()
                if 'матем' in q_text_lower:
                    current_user.ege_math = score
                elif 'русс' in q_text_lower or 'русский' in q_text_lower:
                    current_user.ege_russian = score
                elif 'физ' in q_text_lower:
                    current_user.ege_physics = score
                # Добавляем в список для отображения (в том виде, как ввёл пользователь)
                results_parts.append(f"{question.text}: {score}")
            # Формируем текст результата для сохранения (например, перечисление баллов)
            result_text = "Баллы ЕГЭ — " + "; ".join(results_parts)
            # Сохраняем изменения в профиле пользователя и результат теста
            db.session.add(Result(user_id=current_user.id, test_id=test.id, result_text=result_text))
            db.session.commit()
            flash('Баллы ЕГЭ сохранены.', 'success')
            # После заполнения баллов ЕГЭ перенаправим на главную или к профориентационному тесту
            return redirect(url_for('main.index'))
        else:
            # Обработка профориентационного теста (career)
            categories_score = {}  # словарь суммарных баллов по категориям интересов
            for question in test.questions:
                field_name = f"q_{question.id}"
                selected_option_id = request.form.get(field_name)
                if selected_option_id is None:
                    flash('Пожалуйста, ответьте на все вопросы теста.', 'warning')
                    return render_template('test.html', test=test)
                option = Option.query.get(int(selected_option_id))
                if option is None:
                    continue
                # Добавляем балл за выбранный вариант ответа в категорию
                cat = option.category or "None"
                categories_score[cat] = categories_score.get(cat, 0) + option.score
            # Определяем ведущую категорию интересов пользователя
            interest_category = None
            if categories_score:
                # категория с максимальным суммарным баллом
                interest_category = max(categories_score, key=categories_score.get)
            # Сохраняем интересы пользователя (например, название категории)
            if interest_category:
                current_user.interests = interest_category
            # Формируем рекомендацию с учётом баллов ЕГЭ пользователя
            recommendation = ""
            if interest_category:
                cat_low = interest_category.lower()
                # Примеры рекомендаций для технической и гуманитарной направленности:
                if "тех" in cat_low or "tech" in cat_low:  # технические интересы
                    if current_user.ege_math and current_user.ege_math >= 80 and current_user.ege_physics and current_user.ege_physics >= 80:
                        recommendation = "Рекомендуемые направления: инженерия, информационные технологии, программирование."
                    else:
                        recommendation = "У вас выражен интерес к технической сфере. Однако результаты ЕГЭ по профильным предметам относительно невысоки – стоит уделить внимание их улучшению."
                elif "гум" in cat_low or "human" in cat_low:  # гуманитарные интересы
                    if current_user.ege_russian and current_user.ege_russian >= 80:
                        recommendation = "Рекомендуемые направления: филология, журналистика, юриспруденция."
                    else:
                        recommendation = "У вас выражен интерес к гуманитарной сфере. Для успешной реализации рекомендуется улучшить знания по профильным предметам."
                else:
                    # Общая рекомендация, если категория не распознана в шаблоне
                    recommendation = f"Рекомендуемые направления обучения: {interest_category}."
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
    return render_template('result.html', test=test, result=result)


@main_bp.route('/profile')
@login_required
def profile():
    """Личный профиль с результатами всех тестов."""
    user_results = Result.query.filter_by(user_id=current_user.id).order_by(Result.timestamp.desc()).all()
    career_test = Test.query.filter_by(type='career').first()
    career_id = career_test.id if career_test else None
return render_template('profile.html', results=user_results, career_test_id=career_id)