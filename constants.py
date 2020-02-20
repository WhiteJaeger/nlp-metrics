from rouge import Rouge
from nltk.translate.gleu_score import sentence_gleu, corpus_gleu
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
from nltk.translate.chrf_score import sentence_chrf, corpus_chrf
from nltk.translate.nist_score import sentence_nist, corpus_nist
from nltk.translate.meteor_score import single_meteor_score, meteor_score


ROUGE = Rouge()


METRICS = {
    'bleu': 'BLEU',
    'gleu': 'GLEU',
    'chrf': 'Character n-gram F-score',
    'nist': 'NIST',
    'meteor': 'METEOR',
    'rouge': 'ROUGE'
}


METRICS_MAP = {
    'bleu': sentence_bleu,
    'gleu': sentence_gleu,
    'chrf': sentence_chrf,
    'nist': sentence_nist,
    'meteor': single_meteor_score,
    'rouge': ROUGE.get_scores
}
