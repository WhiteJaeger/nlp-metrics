from flask import Blueprint, render_template, request, send_from_directory, json

bp = Blueprint('stm', __name__, url_prefix='/')


@bp.route('/stm')
def stm():
    return render_template('stm.html',
                           title='STM',
                           legend='Subtree Metric')


def construct_summary_file(data: dict):
    print(data)
    return 'OK'


@bp.route('/api/download-summary', methods=['POST'])
def download_summary():
    construct_summary_file(json.loads(request.get_data()))

    return 'OK'
