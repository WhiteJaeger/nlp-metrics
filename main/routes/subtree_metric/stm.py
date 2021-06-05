from flask import Blueprint, render_template

bp = Blueprint('stm', __name__, url_prefix='/')


@bp.route('/stm')
def stm():
    return render_template('stm.html',
                           title='STM',
                           legend='Subtree Metric')
