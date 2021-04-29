import os

import spacy
from joblib import load
from sklearn.pipeline import Pipeline

# Load SpaCy model
MODEL: spacy.Language = spacy.load('en_core_web_md')

# Load pre-trained POS Tagger model
crf_model_path = os.path.join('models', 'crfWJSModel.joblib')
POS_TAGGING = load(crf_model_path)

# Load sentiment classifier
SENTIMENT_CLASSIFIER = load(os.path.join('models', 'classifier.joblib'))

# Load genre classifier
GENRE_CLASSIFIER: Pipeline = load(os.path.join('models', 'genre_classifier.joblib'))
