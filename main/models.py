import os

import spacy
from joblib import load
from nltk import NaiveBayesClassifier
from sklearn.pipeline import Pipeline

# Load SpaCy model
MODEL: spacy.Language = spacy.load('en_core_web_md')

# Load pre-trained POS Tagger model
POS_TAGGING = load(os.path.join('models', 'crfWJSModel.joblib'))

# Load sentiment classifier
SENTIMENT_CLASSIFIER: NaiveBayesClassifier = load(os.path.join('models', 'sentiment_classifier.joblib'))

# Load genre classifier
GENRE_CLASSIFIER: Pipeline = load(os.path.join('models', 'genre_classifier.joblib'))
