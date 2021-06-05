import os

import flask_restful as restful
from flask import request, json
from spacy import displacy

from main.models import MODEL
from main.utils import generate_salt, purge_old_files


class SentenceTreesAPI(restful.Resource):

    def post(self):
        sentence = json.loads(request.get_data().decode('utf-8'))['text']

        doc = MODEL(sentence)

        svg_dir = os.path.join('static', 'images')

        output_path = os.path.join(svg_dir, f'syntax_tree_{generate_salt()}.svg')
        svg_tree = displacy.render(doc, style='dep', options={'bg': '#fafafa'})

        purge_old_files(svg_dir)

        with open(output_path, 'w', encoding='utf-8') as tree_file:
            tree_file.write(svg_tree)

        output = {
            'text': sentence,
            'syntax_tree_svg_path': output_path
        }

        return json.dumps(output)
