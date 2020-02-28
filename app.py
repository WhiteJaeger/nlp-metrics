import secrets
from flask import Flask, render_template, redirect, url_for, request
from forms import InputForm
from os import path, getenv
from constants import METRICS_MAP, METRICS_FUNCTIONS
from joblib import load
from utils import write_to_file, read_file
import pathlib

from NLP.text_utils import prepare_text


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

    # TODO: add text pre-processing?
    if metric == 'rouge' or metric == 'meteor' or metric == 'chrf':
        hyp = request.form.get('text_hypothesis')
        ref = request.form.get('text_reference')
        result = METRICS_FUNCTIONS[metric](ref, hyp)
    else:
        hyp = request.form.get('text_hypothesis').split()
        ref = request.form.get('text_reference').split()
        result = METRICS_FUNCTIONS[metric]([ref], hyp)

    output = {
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
    data = request.form.get('text_pos')

    data_prepared = prepare_text(data, pos_preparation=True, special_char_removal=False)
    predicted_pos = CRF_MODEL.predict(data_prepared)

    output = {
        'sentence': data,
        'pos': predicted_pos
    }
    write_to_file(output)

    return redirect(url_for('pos'))

# if __name__ == '__main__':
#     serve(APP, host='0.0.0.0', port=8080)
