from flask import Flask
from os import getenv
import secrets
import nltk
import sklearn
from sklearn_crfsuite import CRF
from NLP.pos import prepareData, features


def create_app():
    # Setup flask app
    app = Flask(__name__)
    app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())

    # Setup pos-tagger
    tagged_sentence = nltk.corpus.treebank.tagged_sents(tagset='universal')
    train_set, test_set = sklearn.model_selection.train_test_split(tagged_sentence, test_size=0.05, random_state=1234)
    X_train, y_train = prepareData(train_set)
    crf = CRF(
        algorithm='lbfgs',
        c1=0.01,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    crf.fit(X_train, y_train)

    return app, crf


# _, crf_ = create_app()
# data = [['It', 'is', 'a', 'guide', 'to', 'action', 'that', 'ensures', 'that', 'the', 'military', 'will',
#          'forever', 'heed', 'Party', 'commands']]
# data_prepared = []
# for sentences in data:
#     data_prepared.append([features(sentences, index) for index in range(len(sentences))])
#
# y_pred_new = crf_.predict(data_prepared)
# print(y_pred_new[0])

