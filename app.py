import os
import pathlib
import secrets

import spacy
from flask import Flask, redirect, render_template, request, url_for
from joblib import load
from spacy import displacy
from waitress import serve

from NLP.constants import METRICS_FUNCTIONS, METRICS_MAP
from NLP.text_utils import map_word_pos, prepare_str
from forms import InputForm
from utils import read_tmp_file, write_to_tmp_file, generate_salt


def create_app():
    project_path = str(pathlib.Path(__file__).parents[0])

    # Load pre-trained POS Tagger model
    crf_model_path = os.path.join(project_path, 'models', 'crfWJSModel.joblib')
    crf = load(crf_model_path)

    # Load SpaCy model
    spacy_model: spacy.Language = spacy.load('en_core_web_md')

    # Create images directory
    os.makedirs(os.path.join('static', 'images'), exist_ok=True)

    # Setup flask app
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_urlsafe())
    # Max of 5MB
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # Allowed ext
    app.config['UPLOAD_EXTENSIONS'] = ['.txt']
    # Uploads folder
    os.makedirs('uploads', exist_ok=True)
    app.config['UPLOAD_PATH'] = 'uploads'

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

    return render_template('sentence-trees.html',
                           legend='Sentence Trees',
                           title='Sentence Trees',
                           form=form,
                           output=output)


@APP.route('/api/process-sentence-tree', methods=['POST'])
def process_sentence_tree():
    sentence = request.form.get('text_tree')

    doc = MODEL(sentence)

    svg_dir = os.path.join('static', 'images')

    output_path = os.path.join(svg_dir, f'syntax_tree_{generate_salt()}.svg')
    svg_tree = displacy.render(doc, style='dep', options={'bg': '#fafafa'})

    old_svgs = os.listdir(os.path.dirname(output_path))
    if len(old_svgs) > 10:
        for old_svg in old_svgs:
            os.remove(os.path.join(svg_dir, old_svg))

    with open(output_path, 'w', encoding='utf-8') as tree_file:
        tree_file.write(svg_tree)

    output = {
        'sentence': sentence,
        'syntax_tree_svg_path': output_path
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

    result = METRICS_FUNCTIONS['stm'](ref, hyp, MODEL)

    output = {
        'ref': data['ref'],
        'hyp': data['hyp'],
        'metric': 'STM',
        'value': result
    }
    write_to_tmp_file(output)
    return redirect(url_for('stm'))


@APP.route('/api/handle-stm-corpus', methods=['POST'])
def process_stm_corpus():
    # TODO: MAKE SAFE
    hypotheses_file = request.files['hypothesis-file']
    references_file = request.files['references-file']

    # TODO: Make file names unique
    hypotheses_file.save(os.path.join('uploads', hypotheses_file.filename))
    references_file.save(os.path.join('uploads', references_file.filename))

    # with open(os.path.join('uploads', hypotheses_file.filename), 'r') as f:
    #     print(f.read())

    return redirect(url_for('stm'))


if __name__ == '__main__':
    serve(APP, host='0.0.0.0', port=5000)
