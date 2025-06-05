from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from .ege_programs import EGE_PROGRAMS

calc_bp = Blueprint('calc', __name__)

@calc_bp.route('/ege_calculator', methods=['GET', 'POST'])
@login_required
def ege_calculator():
    scores = {
        'math': current_user.ege_math or 0,
        'russian': current_user.ege_russian or 0,
        'physics': current_user.ege_physics or 0,
    }
    if request.method == 'POST':
        for key in scores:
            try:
                scores[key] = int(request.form.get(f'ege_{key}', 0))
            except ValueError:
                scores[key] = 0
    total = scores['math'] + scores['russian'] + scores['physics']
    programs = []
    for p in EGE_PROGRAMS:
        needed = p['score_2024']
        eligible = False
        if needed is not None and total >= needed:
            eligible = True
        programs.append({**p, 'eligible': eligible})
    return render_template('calculator.html', scores=scores, total=total, programs=programs)
