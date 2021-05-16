import os
from pathlib import Path

import spacy
from joblib import load
from nltk import NaiveBayesClassifier
from sklearn.pipeline import Pipeline

# Get path to the models folder
APP_ROOT = Path(os.path.dirname(__file__)).parent
PATH_TO_MODELS = os.path.join(APP_ROOT, 'models')

# Load SpaCy model
MODEL: spacy.Language = spacy.load('en_core_web_md')

# Load pre-trained POS Tagger model
POS_TAGGING = load(os.path.join(PATH_TO_MODELS, 'crfWJSModel.joblib'))

# Load sentiment classifier
SENTIMENT_CLASSIFIER: NaiveBayesClassifier = load(os.path.join(PATH_TO_MODELS, 'sentiment_classifier.joblib'))

# Load genre classifier
GENRE_CLASSIFIER: Pipeline = load(os.path.join(PATH_TO_MODELS, 'genre_classifier.joblib'))
