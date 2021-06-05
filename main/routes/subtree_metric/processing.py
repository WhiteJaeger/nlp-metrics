import os

import flask_restful as restful
from flask import request, json, current_app
from spacy import displacy
from werkzeug.datastructures import ImmutableMultiDict, MultiDict

from NLP.constants import METRICS_FUNCTIONS
from NLP.text_utils import prepare_str
from main.models import MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER
from main.utils import generate_salt, purge_old_files


class SubtreeMetricAPI(restful.Resource):

    @staticmethod
    def _handle_sentence_level(data: ImmutableMultiDict):
        preprocessing = json.loads(data['preprocessing'])
        text_preparation_params = {k: bool(preprocessing[k]) for k in preprocessing}
        depth = int(data['depth'])

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
            'score': score,
            'depth': depth,
            'isSentimentEnabled': data['isSentimentEnabled'],
            'reference_syntax_tree_path': output_path_ref,
            'hypothesis_syntax_tree_path': output_path_hyp
        }
        return json.dumps(output)

    @staticmethod
    def _handle_corpus_level(data: ImmutableMultiDict, files: MultiDict):
        genre = None
        enable_genre_analyzer = data.get('isGenreEnabled')
        enable_sentiment_analyzer = data.get('isSentimentEnabled')

        preprocessing = json.loads(data.get('preprocessing'))
        text_preparation_params = {k: bool(preprocessing[k]) for k in preprocessing}

        depth = int(data.get('depth'))
        hypotheses_file = files['hypothesis']
        references_file = files['reference']

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

        if enable_genre_analyzer and enable_sentiment_analyzer:
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        sentiment_classifier=SENTIMENT_CLASSIFIER,
                                                        genre_classifier=GENRE_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']
            genre: dict = result['genre']
        elif enable_sentiment_analyzer:
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        sentiment_classifier=SENTIMENT_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']
            genre: dict = result['genre']
        elif enable_genre_analyzer:
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        genre_classifier=GENRE_CLASSIFIER,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']
            genre: dict = result['genre']
        else:
            result = METRICS_FUNCTIONS['stm_augmented'](references=corpora['references'],
                                                        hypotheses=corpora['hypotheses'],
                                                        nlp_model=MODEL,
                                                        depth=depth)
            score = result['score']
            per_sentence_report = result['per_sentence_summary']

        output = {
            'score': score,
            'depth': depth,
            'isGenreEnabled': enable_genre_analyzer,
            'isSentimentEnabled': enable_sentiment_analyzer,
            'per_sentence_summary': get_pairs_with_lowest_scores(per_sentence_report) if per_sentence_report else None,
            'corpora_genres': genre
        }
        return json.dumps(output)

    def post(self):
        if request.form.get('type') == 'sentence-level':
            return self._handle_sentence_level(request.form)
        elif request.form.get('type') == 'corpus-level':
            return self._handle_corpus_level(request.form, request.files)


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
