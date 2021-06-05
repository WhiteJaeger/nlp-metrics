from flask import Blueprint, render_template

bp = Blueprint('sentence_trees', __name__, url_prefix='/')


@bp.route('/sentence-trees')
def sentence_trees():
    return render_template('sentence-trees.html',
                           legend='Sentence Trees Builder',
                           title='Sentence Trees')
