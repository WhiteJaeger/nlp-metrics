from flask import Blueprint, render_template, request, redirect, url_for

from NLP.text_utils import prepare_str, map_word_pos
from forms import InputForm
from main.models import POS_TAGGING
from utils import read_tmp_file, write_to_tmp_file

bp = Blueprint('pos', __name__, url_prefix='/')


@bp.route('/pos-tagger')
def pos():
    form = InputForm()
    output = read_tmp_file()
    return render_template('pos.html',
                           form=form,
                           title='POS Tagger',
                           legend='Context POS Tagger',
                           output=output)


@bp.route('/api/handle-pos-input', methods=['POST'])
def process_pos():
    data = prepare_str(request.form.get('text_pos'), special_char_removal=True)

    data_prepared = prepare_str(data, pos_preparation=True)
    predicted_pos = POS_TAGGING.predict(data_prepared)[0]

    output = {
        'text': data,
        'pos': map_word_pos(data, predicted_pos)
    }
    write_to_tmp_file(output)

    return redirect(url_for('pos.pos'))
