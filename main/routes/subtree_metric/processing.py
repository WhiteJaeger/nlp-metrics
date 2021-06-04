from flask import request, json, current_app

from NLP.text_utils import prepare_str
import flask_restful as restful

import os

from spacy import displacy

from NLP.constants import METRICS_FUNCTIONS, METRICS_MAP
from main.models import MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER
from main.utils import generate_salt, purge_old_files


class SubtreeMetricAPI(restful.Resource):

    def post(self):

        data = json.loads(request.get_data().decode('utf-8'))
        preprocessing = data['preprocessing']
        depth = int(data['depth'])

        text_preparation_params = {
            'contractions': bool(preprocessing.get('contractions')),
            'spec-chars': bool(preprocessing.get('spec-chars')),
            'lowercase': bool(preprocessing.get('lowercase'))
        }

        ref: str = prepare_str(data['reference'],
                               special_char_removal=text_preparation_params['spec-chars'],
                               text_lower_case=text_preparation_params['lowercase'],
                               contraction_expansion=text_preparation_params['contractions'])
        hyp: str = prepare_str(data['hypothesis'],
                               special_char_removal=text_preparation_params['spec-chars'],
                               text_lower_case=text_preparation_params['lowercase'],
                               contraction_expansion=text_preparation_params['contractions'])

        if int(data['isSentimentEnabled']):
            result = METRICS_FUNCTIONS['stm_augmented'](references=[ref],
                                                        hypotheses=[hyp],
                                                        nlp_model=MODEL,
                                                        sentiment_classifier=SENTIMENT_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
        else:
            score = METRICS_FUNCTIONS['stm'](ref, hyp, MODEL, depth)

        # Save syntax trees
        svg_dir = os.path.join('static', 'images')
        purge_old_files(svg_dir)

        parsed_hyp = MODEL(hyp)
        output_path_hyp = os.path.join(svg_dir, f'syntax_tree_hyp_{generate_salt()}.svg')
        svg_tree_hyp = displacy.render(parsed_hyp, style='dep', options={'bg': '#fafafa', 'compact': True})
        with open(output_path_hyp, 'w', encoding='utf-8') as tree_file:
            tree_file.write(svg_tree_hyp)

        parsed_ref = MODEL(ref)
        output_path_ref = os.path.join(svg_dir, f'syntax_tree_ref_{generate_salt()}.svg')
        svg_tree_ref = displacy.render(parsed_ref, style='dep', options={'bg': '#fafafa', 'compact': True})
        with open(output_path_ref, 'w', encoding='utf-8') as tree_file:
            tree_file.write(svg_tree_ref)

        output = {
            'reference': data['reference'],
            'hypothesis': data['hypothesis'],
            'metric': 'STM',
            'score': score,
            'depth': depth,
            'isSentimentEnabled': data['isSentimentEnabled'],
            'reference_syntax_tree_path': output_path_ref,
            'hypothesis_syntax_tree_path': output_path_hyp
        }
        return json.dumps(output)

        # TODO: CORPUS
        genre = None

        text_preparation_params = {
            'contractions': bool(request.form.get('contractions', 0)),
            'spec-chars': bool(request.form.get('spec-chars', 0)),
            'lowercase': bool(request.form.get('lowercase', 0))
        }

        depth = int(request.form.get('depth'))
        hypotheses_file = request.files['hypothesis-file']
        references_file = request.files['references-file']

        # Rm old files
        purge_old_files(current_app.config['UPLOAD_PATH'])

        # Save hypotheses file
        # if not secure_filename(hypotheses_file.filename).split('.')[-1] in APP.config['UPLOAD_EXTENSIONS']:
        #     # TODO: error handling
        #     raise Exception
        hypotheses_file_name = f'{generate_salt()}.txt'
        hypotheses_file.save(os.path.join(current_app.config['UPLOAD_PATH'], hypotheses_file_name))

        # Save references file
        references_file_name = f'{generate_salt()}.txt'
        references_file.save(os.path.join(current_app.config['UPLOAD_PATH'], references_file_name))

        # Read corpora
        corpora = read_corpora(hypotheses_file_name, references_file_name)

        # TODO: Introduce errors
        if not are_corpora_structure_correct(corpora):
            pass

        # Prepare corpora
        corpora = prepare_corpora(corpora, text_preparation_params)

        # TODO: Rollback if something is wrong
        if not are_corpora_structure_correct(corpora):
            pass

        if request.form.get('genre') and request.form.get('sentiment'):
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        sentiment_classifier=SENTIMENT_CLASSIFIER,
                                                        genre_classifier=GENRE_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']
            genre = result['genre']
        elif request.form.get('sentiment'):
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        sentiment_classifier=SENTIMENT_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']
            genre = result['genre']
        elif request.form.get('genre'):
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        genre_classifier=GENRE_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']
            genre = result['genre']
        else:
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']

        output = {
            'metric': 'STM',
            'value': score,
            'depth': depth,
            'genre': request.form.get('genre'),
            'sentiment': request.form.get('sentiment'),
            'per_sentence_summary': get_pairs_with_lowest_scores(per_sentence_report) if per_sentence_report else None,
            'corpora_genre': genre
        }
        # data = json.loads(request.get_data().decode('utf-8'))
        # metric = data['metric']
        # preprocessing = data['preprocessing']
        #
        # text_preparation_params = {
        #     'contractions': bool(preprocessing.get('contractions')),
        #     'spec-chars': bool(preprocessing.get('spec-chars')),
        #     'lowercase': bool(preprocessing.get('lowercase'))
        # }
        #
        # ref = prepare_str(data['reference'],
        #                   text_lower_case=text_preparation_params['lowercase'],
        #                   special_char_removal=text_preparation_params['spec-chars'],
        #                   contraction_expansion=text_preparation_params['contractions'])
        # hyp = prepare_str(data['hypothesis'],
        #                   text_lower_case=text_preparation_params['lowercase'],
        #                   special_char_removal=text_preparation_params['spec-chars'],
        #                   contraction_expansion=text_preparation_params['contractions'])
        #
        # if metric in ('rouge', 'meteor', 'chrf'):
        #     result = METRICS_FUNCTIONS[metric](ref, hyp)
        # else:
        #     hyp = hyp.split()
        #     ref = ref.split()
        #     result = METRICS_FUNCTIONS[metric]([ref], hyp)
        #
        # output = {
        #     'reference': data['reference'],
        #     'hypothesis': data['hypothesis'],
        #     'metric': METRICS_MAP[metric],
        #     'score': result if result > .001 else 0
        # }
        #
        # return json.dumps(output)


def read_corpora(hypotheses_file_name: str, references_file_name: str) -> dict:
    corpora = {}

    with open(os.path.join(current_app.config['UPLOAD_PATH'], hypotheses_file_name), 'r') as f:
        corpora['hypotheses'] = f.read().split('. ')
        while '' in corpora['hypotheses']:
            corpora['hypotheses'].remove('')

    with open(os.path.join(current_app.config['UPLOAD_PATH'], references_file_name), 'r') as f:
        corpora['references'] = f.read().split('. ')
        while '' in corpora['references']:
            corpora['references'].remove('')

    return corpora


def prepare_corpora(corpora: dict[str, str], params: dict[str, bool]) -> dict[str, list[str]]:
    result = {'references': [prepare_str(text,
                                         contraction_expansion=params['contractions'],
                                         text_lower_case=params['lowercase'],
                                         special_char_removal=params['spec-chars'])
                             for text in corpora['references']],
              'hypotheses': [prepare_str(text,
                                         contraction_expansion=params['contractions'],
                                         text_lower_case=params['lowercase'],
                                         special_char_removal=params['spec-chars'])
                             for text in corpora['hypotheses']]
              }
    return result


def are_corpora_structure_correct(corpora: dict) -> bool:
    return len(corpora['hypotheses']) == len(corpora['references'])


def get_pairs_with_lowest_scores(summary: list[dict], k: int = 5) -> list[dict]:
    return sorted(summary, key=lambda x: x['score'])[:k]
