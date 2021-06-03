from flask import Blueprint, render_template

bp = Blueprint('pos', __name__, url_prefix='/')


@bp.route('/pos-tagger')
def pos():
    return render_template('pos.html',
                           title='POS Tagger',
                           legend='Context POS Tagger')
