from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from .ege_programs import EGE_PROGRAMS

SUBJECT_MAP = {
    'М': 'math',
    'Р': 'russian',
    'Ф': 'physics',
    'И': 'informatics',
    'Х': 'chemistry',
    'О': 'social',
    'А': 'language',
}

SUBJECT_NAMES = {
    'math': 'Математика',
    'russian': 'Русский язык',
    'physics': 'Физика',
    'informatics': 'Информатика',
    'chemistry': 'Химия',
    'social': 'Обществознание',
    'language': 'Иностранный язык',
}


def parse_subjects(subject_str):
    groups = []
    for part in subject_str.split('+'):
        options = []
        for token in part.split('/'):
            token = token.strip()
            name = SUBJECT_MAP.get(token)
            if name:
                options.append(name)
        if options:
            groups.append(options)
    return groups


def full_subjects(subject_str):
    parts = []
    for part in subject_str.split('+'):
        names = []
        for token in part.split('/'):
            token = token.strip()
            key = SUBJECT_MAP.get(token)
            full = SUBJECT_NAMES.get(key, token)
            names.append(full)
        parts.append('/'.join(names))
    return ' + '.join(parts)


def calc_program_score(groups, scores):
    total = 0
    for opts in groups:
        total += max(scores.get(o, 0) for o in opts)
    return total

calc_bp = Blueprint('calc', __name__)

@calc_bp.route('/ege_calculator', methods=['GET', 'POST'])
@login_required
def ege_calculator():
    scores = {
        'math': current_user.ege_math or 0,
        'russian': current_user.ege_russian or 0,
        'physics': current_user.ege_physics or 0,
        'informatics': 0,
        'chemistry': 0,
        'social': 0,
        'language': 0,
    }
    if request.method == 'POST':
        for key in scores:
            try:
                scores[key] = int(request.form.get(f'ege_{key}', 0))
            except ValueError:
                scores[key] = 0

    programs = []
    for p in EGE_PROGRAMS:
        groups = parse_subjects(p['subjects'])
        user_score = calc_program_score(groups, scores)
        needed = p['score_2024']
        eligible = needed is not None and user_score >= needed
        probability = None
        if needed is not None:
            probability = max(0, min(100, round((user_score - needed + 30) / 60 * 100, 1)))
        prob_color = None
        if probability is not None:
            if probability >= 60:
                prob_color = 'bg-success'
            elif probability >= 30:
                prob_color = 'bg-warning'
            else:
                prob_color = 'bg-danger'
        cost_display = f"{p['cost']:,}".replace(',', ' ') + ' руб/сем'
        programs.append({
            **p,
            'eligible': eligible,
            'user_score': user_score,
            'probability': probability,
            'prob_color': prob_color,
            'cost_display': cost_display,
            'subjects_full': full_subjects(p['subjects']),
        })

    return render_template('calculator.html', scores=scores, programs=programs)
