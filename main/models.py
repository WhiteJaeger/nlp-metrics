import os

import spacy
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from joblib import load

# Load SpaCy model
MODEL: spacy.Language = spacy.load('en_core_web_md')

# Load pre-trained POS Tagger model
crf_model_path = os.path.join('models', 'crfWJSModel.joblib')
POS_TAGGING = load(crf_model_path)

# Load sentiment analysis model
tokenizer = AutoTokenizer.from_pretrained("lordtt13/emo-mobilebert")

model = AutoModelForSequenceClassification.from_pretrained("lordtt13/emo-mobilebert")

SENTIMENT_MODEL = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
print(SENTIMENT_MODEL("Nothing to see here."))
print(SENTIMENT_MODEL("Nothing to see here.")[0]['label'])
