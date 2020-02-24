import secrets
from flask import Flask, render_template, redirect, url_for, request, json
from forms import InputForm
from os import getenv, path, remove
from waitress import serve
from constants import METRICS_MAP, METRICS_FUNCTIONS
from NLP.text_utils import prepare_text


app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())


@app.route('/')
def hello_world():
    return render_template('home.html', title='Home Page')


@app.route('/metrics-sentence-level')
def sl_metrics():
    form = InputForm()
    output = read_metric_file()

    return render_template('metrics.html',
                           form=form,
                           title='Metrics',
                           legend='Some Legend Example',
                           metric_info=output,
                           metrics=METRICS_MAP)


@app.route('/api/handle-input', methods=['POST'])
def process_input():

    metric = request.form.get('metric')

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
    with open('temp.json', 'w') as temp:
        json.dump(output, temp)
    return redirect(url_for('sl_metrics'))


def read_metric_file():
    data = None

    # TODO: refactor
    if path.exists('temp.json'):
        with open('temp.json', 'r') as temp:
            data = json.load(temp)
        remove('temp.json')

    return data


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
