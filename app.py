import pathlib
import secrets
from os import getenv, path

from flask import Flask, redirect, render_template, request, url_for
from joblib import load
from nltk.chunk.util import conllstr2tree, tree2conllstr
from waitress import serve
import spacy
from spacy import displacy

from NLP.constants import METRICS_FUNCTIONS, METRICS_MAP
from NLP.sentence_tree_builder import SENTENCE_TREE_BUILDER
from NLP.text_utils import map_word_pos, prepare_str
from forms import InputForm
from utils import read_tmp_file, write_to_tmp_file, generate_salt


def create_app():
    project_path = str(pathlib.Path(__file__).parents[0])

    # Load pre-trained POS Tagger model
    crf_model_path = path.join(project_path, 'models', 'crfWJSModel.joblib')
    crf = load(crf_model_path)

    # Load SpaCy model
    spacy_model: spacy.Language = spacy.load('en_core_web_sm')

    # Setup flask app
    app = Flask(__name__)
    app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())

    return app, crf, spacy_model


APP, POS_TAGGING, MODEL = create_app()


@APP.route('/')
def home_page():
    return render_template('home.html', title='Home Page')


# Metrics part
@APP.route('/metrics-sentence-level')
def sl_metrics():
    form = InputForm()
    metric_info = read_tmp_file()

    return render_template('metrics.html',
                           form=form,
                           title='Metrics',
                           legend='Sentence Level Metrics Evaluator',
                           metric_info=metric_info,
                           metrics=METRICS_MAP)


@APP.route('/api/handle-input', methods=['POST'])
def process_input_metric():
    metric = request.form.get('metric')

    text_preparation_params = {
        'contractions': request.form.get('contractions', 0),
        'spec-chars': request.form.get('spec-chars', 0),
        'lowercase': request.form.get('lowercase', 0)
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
    return redirect(url_for('sl_metrics'))


# POS-tagger part
@APP.route('/pos-tagger')
def pos():
    form = InputForm()
    output = read_tmp_file()
    return render_template('pos.html',
                           form=form,
                           title='POS Tagger',
                           legend='Context POS Tagger',
                           output=output)


@APP.route('/api/handle-pos-input', methods=['POST'])
def process_pos():
    data = prepare_str(request.form.get('text_pos'), special_char_removal=True)

    data_prepared = prepare_str(data, pos_preparation=True)
    predicted_pos = POS_TAGGING.predict(data_prepared)[0]

    output = {
        'text': data,
        'pos': map_word_pos(data, predicted_pos)
    }
    write_to_tmp_file(output)

    return redirect(url_for('pos'))


# Sentence trees part
@APP.route('/sentence-trees')
def sentence_trees():
    form = InputForm()
    output = read_tmp_file()

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

    # prepared_sentence = prepare_str(sentence, pos_preparation=True)
    # pos_tags = POS_TAGGING.predict(prepared_sentence)[0]
    # word_pos = map_word_pos(sentence, pos_tags)
    #
    # sentence_tree = SENTENCE_TREE_BUILDER.parse(word_pos)
    doc = MODEL(sentence)
    output_path = pathlib.Path('')

    output = {
        'sentence': sentence,
        'syntax_tree_svg_path': tree2conllstr(sentence_tree)
    }
    write_to_tmp_file(output)
    return redirect(url_for('sentence_trees'))


# STM part
@APP.route('/stm')
def stm():
    form = InputForm()
    output = read_tmp_file()
    return render_template('stm.html',
                           title='STM',
                           form=form,
                           legend='Subtree Metric',
                           metric_info=output)


@APP.route('/api/handle-stm', methods=['POST'])
def process_stm():
    data = {
        'ref': request.form.get('text_reference'),
        'hyp': request.form.get('text_hypothesis')
    }

    ref = prepare_str(data['ref'], special_char_removal=True)
    hyp = prepare_str(data['hyp'], special_char_removal=True)

    # ref_prepared = prepare_str(ref)
    # hyp_prepared = prepare_str(hyp)
    # pos_ref = POS_TAGGING.predict(ref_prepared)[0]
    # pos_hyp = POS_TAGGING.predict(hyp_prepared)[0]
    #
    # word_pos_ref = map_word_pos(data['ref'], pos_ref)
    # word_pos_hyp = map_word_pos(data['hyp'], pos_hyp)
    #
    # sentence_tree_ref = SENTENCE_TREE_BUILDER.parse(word_pos_ref)
    # sentence_tree_hyp = SENTENCE_TREE_BUILDER.parse(word_pos_hyp)

    result = METRICS_FUNCTIONS['stm'](ref, hyp, MODEL)

    output = {
        'ref': data['ref'],
        'hyp': data['hyp'],
        'metric': 'STM',
        'value': result
    }
    write_to_tmp_file(output)
    return redirect(url_for('stm'))


if __name__ == '__main__':
    serve(APP, host='0.0.0.0', port=5000)
