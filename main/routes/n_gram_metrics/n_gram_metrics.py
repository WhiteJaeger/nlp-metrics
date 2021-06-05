from flask import Blueprint, render_template

from NLP.constants import METRICS_MAP

bp = Blueprint('metrics', __name__, url_prefix='/')


@bp.route('/n-gram-metrics')
def n_gram_metrics():
    return render_template('metrics.html',
                           title='Metrics',
                           legend='Sentence Level Metrics Evaluator',
                           metrics=METRICS_MAP)
