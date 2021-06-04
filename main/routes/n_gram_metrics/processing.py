from flask import request, json

from NLP.constants import METRICS_FUNCTIONS, METRICS_MAP
from NLP.text_utils import prepare_str
import flask_restful as restful


class NGramMetricsAPI(restful.Resource):

    def post(self):
        data = json.loads(request.get_data().decode('utf-8'))
        metric = data['metric']

        text_preparation_params = {
            'contractions': bool(data.get('contractions')),
            'spec-chars': bool(data.get('spec-chars')),
            'lowercase': bool(data.get('lowercase'))
        }

        ref = prepare_str(data['reference'],
                          text_lower_case=text_preparation_params['lowercase'],
                          special_char_removal=text_preparation_params['spec-chars'],
                          contraction_expansion=text_preparation_params['contractions'])
        hyp = prepare_str(data['hypothesis'],
                          text_lower_case=text_preparation_params['lowercase'],
                          special_char_removal=text_preparation_params['spec-chars'],
                          contraction_expansion=text_preparation_params['contractions'])

        if metric in ('rouge', 'meteor', 'chrf'):
            result = METRICS_FUNCTIONS[metric](ref, hyp)
        else:
            hyp = hyp.split()
            ref = ref.split()
            result = METRICS_FUNCTIONS[metric]([ref], hyp)

        output = {
            'reference': data['reference'],
            'hypothesis': data['hypothesis'],
            'metric': METRICS_MAP[metric],
            'score': result if result > .001 else 0
        }

        return json.dumps(output)
