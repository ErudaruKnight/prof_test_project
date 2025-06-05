from app.career_utils import (
    load_structure,
    calculate_interest_scores,
    order_scores,
    recommend_program,
)


def test_load_structure():
    questions, programs = load_structure()
    assert len(questions) == 30
    assert "Информатика и вычислительная техника" in programs


def test_calculate_and_recommend():
    questions, programs = load_structure()
    answers = {q["id"]: 0 for q in questions}
    answers[1] = 4
    scores = calculate_interest_scores(questions, answers)
    assert scores["Прикладная математика"] >= 5
    ege = {"math": 100, "russian": 90, "physics": 90, "informatics": 95,
           "chemistry": 0, "social": 0, "language": 0}
    program = recommend_program(scores, ege, programs)
    assert program is not None


def test_order_scores():
    ordered = order_scores({'A': 1, 'B': 3, 'C': 2})
    assert ordered[0] == ('B', 3)
    assert ordered[-1] == ('A', 1)