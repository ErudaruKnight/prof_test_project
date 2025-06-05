import json
import re
from pathlib import Path

from .calc import parse_subjects, calc_program_score

DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "career_test_structure.md"


def load_structure(path: Path = DOC_PATH):
    """Load questions and program table from documentation."""
    text = path.read_text(encoding="utf-8")

    json_match = re.search(r"```json\n(.*?)```", text, re.S)
    if not json_match:
        raise ValueError("JSON block not found in documentation")
    questions = json.loads(json_match.group(1))

    table_match = re.search(r"## Профильные предметы.*?\n((?:\|.*\n)+)", text, re.S)
    programs = {}
    if table_match:
        lines = [ln.strip() for ln in table_match.group(1).strip().splitlines()]
        for line in lines[2:]:
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 3:
                name, subjects, score = cols[0], cols[1], cols[2]
                programs[name] = {
                    "subjects": subjects,
                    "score_2024": int(score) if score not in {"—", "-", ""} else None,
                }
    return questions, programs


def calculate_interest_scores(questions, answers):
    """Sum weights for each direction based on user's answers.

    Parameters
    ----------
    questions : list
        Question definitions from the structure.
    answers : dict
        Mapping question id -> option index (0-based).
    """
    totals = {}
    for q in questions:
        qid = q["id"]
        idx = answers.get(qid)
        if idx is None:
            continue
        if not (0 <= idx < len(q["options"])):
            continue
        option = q["options"][idx]
        for direction, weight in option["weights"].items():
            totals[direction] = totals.get(direction, 0) + weight
    return totals


def recommend_program(scores, ege_scores, programs):
    """Return best matching program considering EGE scores."""
    if not scores:
        return None
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for direction, _ in ordered:
        info = programs.get(direction)
        if not info:
            continue
        groups = parse_subjects(info["subjects"])
        user_score = calc_program_score(groups, ege_scores)
        needed = info["score_2024"]
        if needed is None or user_score >= needed:
            return direction
    return ordered[0][0]


def ensure_career_test():
    """Make sure a career test record exists in the database."""
    from app.models import Test
    from app import db

    if not Test.query.filter_by(type='career').first():
        t = Test(title='Профориентационный тест', type='career')
        db.session.add(t)
        db.session.commit()
        return t
    return Test.query.filter_by(type='career').first()
