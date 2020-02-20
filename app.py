import secrets
from flask import Flask, render_template, redirect, url_for, request, json
from forms import InputForm
from os import getenv, path, remove
from waitress import serve
from constants import METRICS
from NLP.text_utils import prepare_text


app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())


@app.route('/')
def hello_world():
    return render_template('home.html', title='Home Page')


@app.route('/metrics')
def metrics():
    form = InputForm()
    metric_value = read_metric_file()

    return render_template('metrics.html',
                           form=form,
                           title='Metrics',
                           legend='Some Legend Example',
                           metric_value=metric_value,
                           metrics=METRICS)


@app.route('/api/handle-input', methods=['POST'])
def process_input():
    # TODO: Use prepare_text for specific metrics
    hyp = request.form.get('text_hypothesis')
    ref = request.form.get('text_reference')
    metric = request.form.get('metric')

    # TODO: refactor
    with open('temp.json', 'w') as temp:
        json.dump(metric, temp)
    print(hyp, ref, metric)
    return redirect(url_for('metrics'))


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
