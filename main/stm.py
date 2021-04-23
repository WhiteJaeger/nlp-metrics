import os

from flask import Blueprint, render_template, request, redirect, url_for, current_app

from NLP.constants import METRICS_FUNCTIONS
from NLP.text_utils import prepare_str
from forms import InputForm
from main.models import MODEL
from utils import read_tmp_file, write_to_tmp_file, generate_salt

bp = Blueprint('stm', __name__, url_prefix='/')


@bp.route('/stm')
def stm():
    form = InputForm()
    output = read_tmp_file()
    return render_template('stm.html',
                           title='STM',
                           form=form,
                           legend='Subtree Metric',
                           metric_info=output)


@bp.route('/api/handle-stm', methods=['POST'])
def process_stm():
    data = {
        'ref': request.form.get('text_reference'),
        'hyp': request.form.get('text_hypothesis')
    }

    ref = prepare_str(data['ref'], special_char_removal=True)
    hyp = prepare_str(data['hyp'], special_char_removal=True)

    result = METRICS_FUNCTIONS['stm'](ref, hyp, MODEL)

    output = {
        'ref': data['ref'],
        'hyp': data['hyp'],
        'metric': 'STM',
        'value': result
    }
    write_to_tmp_file(output)
    return redirect(url_for('stm.stm'))


@bp.route('/api/handle-stm-corpus', methods=['POST'])
def process_stm_corpus():
    # TODO: MAKE SAFE
    hypotheses_file = request.files['hypothesis-file']
    references_file = request.files['references-file']

    # Rm old files
    old_corpora = os.listdir('uploads')
    if len(old_corpora) > 20:
        for old_corpus in old_corpora:
            os.remove(os.path.join(current_app.config['UPLOAD_PATH'], old_corpus))

    # Save hypotheses file
    # if not secure_filename(hypotheses_file.filename).split('.')[-1] in APP.config['UPLOAD_EXTENSIONS']:
    #     # TODO: error handling
    #     raise Exception
    hypotheses_file.save(os.path.join(current_app.config['UPLOAD_PATH'], f'{generate_salt()}.txt'))

    # Save references file
    references_file.save(os.path.join(current_app.config['UPLOAD_PATH'], f'{generate_salt()}.txt'))

    # TODO: count score
    # with open(os.path.join('uploads', hypotheses_file.filename), 'r') as f:
    #     print(f.read())

    return redirect(url_for('stm.stm'))
