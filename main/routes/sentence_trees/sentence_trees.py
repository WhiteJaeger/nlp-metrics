import os

from flask import Blueprint, render_template, request, redirect, url_for
from spacy import displacy

from main.forms import InputForm
from main.models import MODEL
from main.utils import read_tmp_file, write_to_tmp_file, generate_salt, purge_old_files

bp = Blueprint('sentence_trees', __name__, url_prefix='/')


@bp.route('/sentence-trees')
def sentence_trees():
    form = InputForm()
    output = read_tmp_file()

    return render_template('sentence-trees.html',
                           legend='Sentence Trees Builder',
                           title='Sentence Trees',
                           form=form,
                           output=output)


@bp.route('/api/process-sentence-tree', methods=['POST'])
def process_sentence_tree():
    sentence = request.form.get('text_tree')

    doc = MODEL(sentence)

    svg_dir = os.path.join('static', 'images')

    output_path = os.path.join(svg_dir, f'syntax_tree_{generate_salt()}.svg')
    svg_tree = displacy.render(doc, style='dep', options={'bg': '#fafafa'})

    purge_old_files(svg_dir)

    with open(output_path, 'w', encoding='utf-8') as tree_file:
        tree_file.write(svg_tree)

    output = {
        'sentence': sentence,
        'syntax_tree_svg_path': output_path
    }
    write_to_tmp_file(output)
    return redirect(url_for('sentence_trees.sentence_trees'))
