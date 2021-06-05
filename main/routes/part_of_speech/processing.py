import flask_restful as restful
from flask import request, json

from NLP.text_utils import prepare_str, map_word_pos
from main.models import POS_TAGGING


class POSAPI(restful.Resource):

    def post(self):
        data = json.loads(request.get_data().decode('utf-8'))['text']
        data_prepared = prepare_str(data, pos_preparation=True)
        predicted_pos = POS_TAGGING.predict(data_prepared)[0]

        output = {
            'text': data,
            'pos': map_word_pos(data, predicted_pos),
        }
        return json.dumps(output)
