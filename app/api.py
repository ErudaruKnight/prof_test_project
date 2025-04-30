from flask import Blueprint, jsonify, abort
from app.models import User, Test, Question, Option, Result

api_bp = Blueprint('api', __name__)

@api_bp.route('/tests', methods=['GET'])
def api_get_tests():
    """API эндпоинт: получить список всех тестов."""
    tests = Test.query.all()
    tests_data = []
    for test in tests:
        tests_data.append({
            "id": test.id,
            "title": test.title,
            "description": test.description or "",
            "type": test.type or ""
        })
    return jsonify({"tests": tests_data})

@api_bp.route('/tests/<int:test_id>', methods=['GET'])
def api_get_test_detail(test_id):
    """API эндпоинт: получить детали теста (вопросы и варианты)."""
    test = Test.query.get_or_404(test_id)
    test_data = {
        "id": test.id,
        "title": test.title,
        "description": test.description or "",
        "type": test.type or "",
        "questions": []
    }
    for q in test.questions:
        q_data = {"id": q.id, "text": q.text, "options": []}
        for opt in q.options:
            q_data["options"].append({
                "id": opt.id,
                "text": opt.text,
                "score": opt.score,
                "category": opt.category or ""
            })
        test_data["questions"].append(q_data)
    return jsonify(test_data)

@api_bp.route('/user/<int:user_id>/results', methods=['GET'])
def api_get_user_results(user_id):
    """API эндпоинт: получить результаты всех тестов для указанного пользователя."""
    user = User.query.get_or_404(user_id)
    results_data = []
    for res in user.results:
        results_data.append({
            "test_id": res.test_id,
            "test_title": res.test.title,
            "result": res.result_text,
            "timestamp": res.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"user": user.username, "results": results_data})
