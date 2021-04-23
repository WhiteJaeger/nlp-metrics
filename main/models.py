import os

import spacy
from joblib import load

# Load SpaCy model
MODEL: spacy.Language = spacy.load('en_core_web_md')

# Load pre-trained POS Tagger model
crf_model_path = os.path.join('models', 'crfWJSModel.joblib')
POS_TAGGING = load(crf_model_path)
