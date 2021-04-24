from flask import Blueprint, render_template, request, redirect, url_for

from NLP.constants import METRICS_FUNCTIONS, METRICS_MAP
from NLP.text_utils import prepare_str
from main.forms import InputForm
from main.utils import read_tmp_file, write_to_tmp_file

bp = Blueprint('metrics', __name__, url_prefix='/')


@bp.route('/metrics-sentence-level')
def sl_metrics():
    form = InputForm()
    metric_info = read_tmp_file()

    return render_template('metrics.html',
                           form=form,
                           title='Metrics',
                           legend='Sentence Level Metrics Evaluator',
                           metric_info=metric_info,
                           metrics=METRICS_MAP)


@bp.route('/api/handle-input', methods=['POST'])
def process_input_metric():
    metric = request.form.get('metric')

    text_preparation_params = {
        'contractions': bool(request.form.get('contractions', 0)),
        'spec-chars': bool(request.form.get('spec-chars', 0)),
        'lowercase': bool(request.form.get('lowercase', 0))
    }

    data = {
        'ref': request.form.get('text_reference'),
        'hyp': request.form.get('text_hypothesis')
    }

    ref = prepare_str(data['ref'],
                      text_lower_case=text_preparation_params['lowercase'],
                      special_char_removal=text_preparation_params['spec-chars'],
                      contraction_expansion=text_preparation_params['contractions'])
    hyp = prepare_str(data['hyp'],
                      text_lower_case=text_preparation_params['lowercase'],
                      special_char_removal=text_preparation_params['spec-chars'],
                      contraction_expansion=text_preparation_params['contractions'])

    if metric in ('rouge', 'meteor', 'chrf'):
        result = METRICS_FUNCTIONS[metric](ref, hyp)
    else:
        hyp = hyp.split()
        ref = ref.split()
        result = METRICS_FUNCTIONS[metric]([ref], hyp)

    output = {
        'ref': data['ref'],
        'hyp': data['hyp'],
        'metric': METRICS_MAP[metric],
        'value': result
    }
    write_to_tmp_file(output)
    return redirect(url_for('metrics.sl_metrics'))
