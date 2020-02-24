import secrets
from flask import render_template, redirect, url_for, request, json
from forms import InputForm
from os import path, remove
from waitress import serve
from constants import METRICS_MAP, METRICS_FUNCTIONS
from NLP.pos import features
# from NLP.text_utils import prepare_text
from . import create_app

app, crf = create_app()


# Metrics part
@app.route('/')
def hello_world():
    return render_template('home.html', title='Home Page')


@app.route('/metrics-sentence-level')
def sl_metrics():
    form = InputForm()
    output = read_temp_file()

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
    write_to_file(output)
    return redirect(url_for('sl_metrics'))


# POS-tagger part
@app.route('/pos-tagger')
def pos():
    form = InputForm()
    output = read_temp_file()
    return render_template('pos.html',
                           form=form,
                           title='POS-tagger',
                           legend='SMTH',
                           output=output)


@app.route('/api/handle-pos-input', methods=['POST'])
def process_pos():
    data = [request.form.get('text_pos').split()]

    data_prepared = []
    for sentences in data:
        data_prepared.append([features(sentences, index) for index in range(len(sentences))])

    predicted_pos = crf.predict(data_prepared)[0]

    output = {
        'sentence': data,
        'pos': predicted_pos
    }
    write_to_file(output)

    return redirect(url_for('pos'))


# Utils
def read_temp_file():
    data = None

    # TODO: refactor
    if path.exists('temp.json'):
        with open('temp.json', 'r') as temp:
            data = json.load(temp)
        remove('temp.json')

    return data


def write_to_file(output):
    with open('temp.json', 'w') as temp:
        json.dump(output, temp)


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
