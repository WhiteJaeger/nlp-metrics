import secrets
from flask import Flask, render_template, redirect, url_for, request
from forms import InputForm
from os import path, getenv
from constants import METRICS_MAP, METRICS_FUNCTIONS
from joblib import load
from utils import write_to_file, read_file
import pathlib

from NLP.text_utils import prepare_str, map_word_pos


def create_app():
    # Load pre-trained model
    project_path = str(pathlib.Path(__file__).parents[0])
    model_path = path.join(project_path, 'models', 'crfWJSModel900k.joblib')
    crf = load(model_path)

    # Setup flask app
    app = Flask(__name__)
    app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())

    return app, crf


APP, CRF_MODEL = create_app()


# Metrics part
@APP.route('/')
def hello_world():
    return render_template('home.html', title='Home Page')


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
        'spec-chars': request.form.get('spec-chars', 0),
        'lowercase': request.form.get('spec-chars', 0)
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
        'sentence': data,
        'pos': map_word_pos(data, predicted_pos)
    }
    write_to_file(output)

    return redirect(url_for('pos'))

# if __name__ == '__main__':
#     serve(APP, host='0.0.0.0', port=8080)
