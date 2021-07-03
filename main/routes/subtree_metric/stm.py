import os
import csv
from flask import Blueprint, render_template, request, send_from_directory, json, current_app
from main.utils import generate_salt, purge_old_files

bp = Blueprint('stm', __name__, url_prefix='/')


@bp.route('/stm')
def stm():
    return render_template('stm.html',
                           title='STM',
                           legend='Subtree Metric')


def construct_summary_file(data: dict) -> str:
    file_name = f'per_sentence_report_depth_{data["depth"]}'

    is_genre_analyzer_enabled = data['genre-analyzer-enabled'] == 'Yes'
    is_sentiment_analyzer_enabled = data['sentiment-analyzer-enabled'] == 'Yes'

    if is_genre_analyzer_enabled:
        file_name += '_genre'
    if is_sentiment_analyzer_enabled:
        file_name += '_sentiment'
    file_name += generate_salt()
    file_name += '.csv'
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], file_name)

    purge_old_files(current_app.config['UPLOAD_PATH'])

    with open(file_path, 'w', encoding='utf-8', newline='') as report_file:
        column_names = ['Hypothesis', 'Reference',
                        'Reference Sentiment', 'Hypothesis Sentiment',
                        'Reference Genre', 'Hypothesis Genre',
                        'STM Score']
        csv_writer = csv.DictWriter(report_file, delimiter=',', lineterminator='\r', fieldnames=column_names)
        csv_writer.writeheader()

        for per_sentence_report in data['per-sentence-reports']:
            csv_writer.writerow({
                'Hypothesis': per_sentence_report['hypothesis-sentence'],
                'Reference': per_sentence_report['reference-sentence'],
                'Reference Sentiment':
                    per_sentence_report['reference-sentence-sentiment'] if is_sentiment_analyzer_enabled else 'NULL',
                'Hypothesis Sentiment':
                    per_sentence_report['hypothesis-sentence-sentiment'] if is_sentiment_analyzer_enabled else 'NULL',
                'Reference Genre':
                    per_sentence_report['reference-sentence-genre'] if is_genre_analyzer_enabled else 'NULL',
                'Hypothesis Genre':
                    per_sentence_report['hypothesis-sentence-genre'] if is_genre_analyzer_enabled else 'NULL',
                'STM Score': per_sentence_report['score']
            })

    return file_name


@bp.route('/api/download-summary', methods=['POST'])
def download_summary():
    file_name = construct_summary_file(json.loads(request.get_data()))

    return send_from_directory(directory=current_app.config['UPLOAD_PATH'], filename=file_name, as_attachment=True)
