import os

import spacy
from flask import Blueprint, render_template, request, redirect, url_for, current_app

from NLP.constants import METRICS_FUNCTIONS
from NLP.text_utils import prepare_str
from main.forms import InputForm
from main.models import MODEL
from main.utils import read_tmp_file, write_to_tmp_file, generate_salt

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

    # TODO: add sentiment

    data = {
        'ref': request.form.get('text_reference'),
        'hyp': request.form.get('text_hypothesis'),
        'depth': int(request.form.get('depth'))
    }

    text_preparation_params = {
        'contractions': bool(request.form.get('contractions', 0)),
        'spec-chars': bool(request.form.get('spec-chars', 0)),
        'lowercase': bool(request.form.get('lowercase', 0))
    }

    ref = prepare_str(data['ref'],
                      special_char_removal=text_preparation_params['spec-chars'],
                      text_lower_case=text_preparation_params['lowercase'],
                      contraction_expansion=text_preparation_params['contractions'])
    hyp = prepare_str(data['hyp'],
                      special_char_removal=text_preparation_params['spec-chars'],
                      text_lower_case=text_preparation_params['lowercase'],
                      contraction_expansion=text_preparation_params['contractions'])

    result = METRICS_FUNCTIONS['stm'](ref, hyp, MODEL, data['depth'])

    output = {
        'ref': data['ref'],
        'hyp': data['hyp'],
        'metric': 'STM',
        'value': result,
        'depth': data['depth']
    }
    write_to_tmp_file(output)
    return redirect(url_for('stm.stm'))


@bp.route('/api/handle-stm-corpus', methods=['POST'])
def process_stm_corpus():
    text_preparation_params = {
        'contractions': bool(request.form.get('contractions', 0)),
        'spec-chars': bool(request.form.get('spec-chars', 0)),
        'lowercase': bool(request.form.get('lowercase', 0))
    }

    depth = int(request.form.get('depth'))
    hypotheses_file = request.files['hypothesis-file']
    references_file = request.files['references-file']

    # Rm old files
    remove_old_corpora()

    # Save hypotheses file
    # if not secure_filename(hypotheses_file.filename).split('.')[-1] in APP.config['UPLOAD_EXTENSIONS']:
    #     # TODO: error handling
    #     raise Exception
    hypotheses_file_name = f'{generate_salt()}.txt'
    hypotheses_file.save(os.path.join(current_app.config['UPLOAD_PATH'], hypotheses_file_name))

    # Save references file
    references_file_name = f'{generate_salt()}.txt'
    references_file.save(os.path.join(current_app.config['UPLOAD_PATH'], references_file_name))

    # Read corpora
    corpora = read_corpora(hypotheses_file_name, references_file_name)

    # TODO: Introduce errors
    if not are_corpora_structure_correct(corpora):
        pass

    # Prepare corpora
    corpora = prepare_corpora(corpora, text_preparation_params)

    # TODO: Rollback if something is wrong
    if not are_corpora_structure_correct(corpora):
        pass

    score = calculate_stm_score_corpora(corpora, MODEL, depth)

    output = {
        'metric': 'STM',
        'value': score,
        'depth': depth
    }
    write_to_tmp_file(output)

    return redirect(url_for('stm.stm'))


def remove_old_corpora():
    old_corpora = os.listdir(current_app.config['UPLOAD_PATH'])
    if len(old_corpora) > 20:
        for old_corpus in old_corpora:
            os.remove(os.path.join(current_app.config['UPLOAD_PATH'], old_corpus))


def read_corpora(hypotheses_file_name: str, references_file_name: str) -> dict:
    corpora = {}

    with open(os.path.join(current_app.config['UPLOAD_PATH'], hypotheses_file_name), 'r') as f:
        corpora['hypotheses'] = f.read().split('. ')
        while '' in corpora['hypotheses']:
            corpora['hypotheses'].remove('')

    with open(os.path.join(current_app.config['UPLOAD_PATH'], references_file_name), 'r') as f:
        corpora['references'] = f.read().split('. ')
        while '' in corpora['references']:
            corpora['references'].remove('')

    return corpora


def prepare_corpora(corpora: dict[str, str], params: dict[str, bool]) -> dict[str, list[str]]:
    result = {'references': [prepare_str(text,
                                         contraction_expansion=params['contractions'],
                                         text_lower_case=params['lowercase'],
                                         special_char_removal=params['spec-chars'])
                             for text in corpora['references']],
              'hypotheses': [prepare_str(text,
                                         contraction_expansion=params['contractions'],
                                         text_lower_case=params['lowercase'],
                                         special_char_removal=params['spec-chars'])
                             for text in corpora['hypotheses']]
              }
    return result


def are_corpora_structure_correct(corpora: dict) -> bool:
    return len(corpora['hypotheses']) == len(corpora['references'])


def calculate_stm_score_corpora(corpora: dict,
                                model: spacy.Language,
                                depth: int) -> float:
    # TODO: add per-sentence report with lowest scores

    score = 0

    for reference_sentence, hypothesis_sentence in zip(corpora['references'], corpora['hypotheses']):
        score += METRICS_FUNCTIONS['stm'](reference_sentence, hypothesis_sentence, model, depth)

    return round(score / len(corpora['references']), 4)
