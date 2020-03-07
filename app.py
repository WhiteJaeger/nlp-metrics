import pathlib
import secrets
from os import getenv, path

from flask import Flask, redirect, render_template, request, url_for
from joblib import load
from nltk.chunk.util import conllstr2tree, tree2conllstr

from NLP.chunker import ntc as SENTENCE_CHUNKER
from NLP.text_utils import map_word_pos, prepare_str
from constants import METRICS_FUNCTIONS, METRICS_MAP
from forms import InputForm
from utils import read_file, write_to_file


def create_app():
    project_path = str(pathlib.Path(__file__).parents[0])

    # Load pre-trained POS Tagger model
    crf_model_path = path.join(project_path, 'models', 'crfWJSModel900k.joblib')
    crf = load(crf_model_path)

    # Setup flask app
    app = Flask(__name__)
    app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())

    return app, crf


APP, CRF_MODEL = create_app()


@APP.route('/')
def hello_world():
    return render_template('home.html', title='Home Page')


# Metrics part
@APP.route('/metrics-sentence-level')
def sl_metrics():
    form = InputForm()
    output = read_file()

    return render_template('metrics.html',
                           form=form,
                           title='Metrics',
                           legend='Sentence Level Metrics Evaluator',
                           metric_info=output,
                           metrics=METRICS_MAP)


@APP.route('/api/handle-input', methods=['POST'])
def process_input_metric():
    metric = request.form.get('metric')

    text_preparation_params = {
            'contractions': request.form.get('contractions', 0),
            'spec-chars'  : request.form.get('spec-chars', 0),
            'lowercase'   : request.form.get('lowercase', 0)
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
            'ref'   : data['ref'],
            'hyp'   : data['hyp'],
            'metric': METRICS_MAP[metric],
            'value' : result
    }
    write_to_file(output)
    return redirect(url_for('sl_metrics'))


# POS-tagger part
@APP.route('/pos-tagger')
def pos():
    form = InputForm()
    output = read_file()
    return render_template('pos.html',
                           form=form,
                           title='POS Tagger',
                           legend='Context POS Tagger',
                           output=output)


@APP.route('/api/handle-pos-input', methods=['POST'])
def process_pos():
    data = prepare_str(request.form.get('text_pos'), special_char_removal=True)

    data_prepared = prepare_str(data, pos_preparation=True)
    predicted_pos = CRF_MODEL.predict(data_prepared)[0]

    output = {
            'text': data,
            'pos' : map_word_pos(data, predicted_pos)
    }
    write_to_file(output)

    return redirect(url_for('pos'))


# Sentence trees part
@APP.route('/sentence-trees')
def sentence_trees():
    form = InputForm()
    output = read_file()
    if output:
        output['sentence_tree'] = conllstr2tree(output['sentence_tree'])
    return render_template('sentence-trees.html',
                           legend='Sentence Trees',
                           title='Sentence Trees',
                           form=form,
                           output=output)


@APP.route('/api/process-sentence-tree', methods=['POST'])
def process_sentence_tree():
    sentence = request.form.get('text_tree')

    prepared_sentence = prepare_str(sentence, pos_preparation=True)
    pos_tags = CRF_MODEL.predict(prepared_sentence)[0]
    word_pos = map_word_pos(sentence, pos_tags)

    sentence_tree = SENTENCE_CHUNKER.parse(word_pos)

    output = {
            'sentence'     : sentence,
            'sentence_tree': tree2conllstr(sentence_tree)
    }
    write_to_file(output)
    return redirect(url_for('sentence_trees'))

# if __name__ == '__main__':
#     serve(APP, host='0.0.0.0', port=8080)
