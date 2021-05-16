import os
from pathlib import Path

import spacy
from joblib import load
from nltk import NaiveBayesClassifier
from sklearn.pipeline import Pipeline

# Load SpaCy model
MODEL: spacy.Language = spacy.load('en_core_web_md')

APP_ROOT = Path(os.path.dirname(__file__)).parent
PATH_TO_MODELS_FOLDER = os.path.join(APP_ROOT, 'models')

# Load pre-trained POS Tagger model
POS_TAGGING = load(os.path.join(PATH_TO_MODELS_FOLDER, 'crfWJSModel.joblib'))

# Load sentiment classifier
SENTIMENT_CLASSIFIER: NaiveBayesClassifier = load(os.path.join(PATH_TO_MODELS_FOLDER, 'sentiment_classifier.joblib'))

# Load genre classifier
GENRE_CLASSIFIER: Pipeline = load(os.path.join(PATH_TO_MODELS_FOLDER, 'genre_classifier.joblib'))
