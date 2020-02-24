import rouge
from nltk.translate.gleu_score import sentence_gleu, corpus_gleu
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
from nltk.translate.chrf_score import sentence_chrf, corpus_chrf
from nltk.translate.nist_score import sentence_nist, corpus_nist
from nltk.translate.meteor_score import single_meteor_score, meteor_score

ref1 = str('It is a guide to action that ensures that the military will forever heed Party commands').split()
# ['PRON', 'VERB', 'DET', 'NOUN', 'PRT', 'NOUN', 'ADP', 'NOUN', 'ADP', 'DET', 'ADJ', 'VERB', 'ADV', 'VERB', 'NOUN', 'VERB']
# PRON VERB DET NOUN PRT NOUN ADP NOUN ADP DET ADJ VERB ADV VERB NOUN VERB
hyp1 = str('It is a guide to action which ensures that the military always obeys the commands of the party').split()
# ['PRON', 'VERB', 'DET', 'NOUN', 'PRT', 'NOUN', 'DET', 'NOUN', 'ADP', 'DET', 'ADJ', 'ADV', 'VERB', 'DET', 'NOUN', 'ADP', 'DET', 'NOUN']
# PRON VERB DET NOUN PRT NOUN DET NOUN ADP DET ADJ ADV VERB DET NOUN ADP DET NOUN
hyp2 = str('It is to insure the troops forever hearing the activity guidebook that party directs').split()
print('1 ', sentence_gleu([ref1], hyp1))
print('2', sentence_gleu([ref1], hyp2))

print('3 ', sentence_bleu([ref1], hyp1))
print('4 ', sentence_bleu([ref1], hyp2, weights=[1/3, 1/3, 1/3]))

print('5 ', sentence_chrf(ref1, hyp1))
print(sentence_chrf(ref1, hyp2))

print('6 ', sentence_nist([ref1], hyp1))
print('7 ', sentence_nist([ref1], hyp2))


ref1 = str('PRON VERB DET NOUN PRT NOUN ADP NOUN ADP DET ADJ VERB ADV VERB NOUN VERB').split()
hyp1 = str('PRON VERB DET NOUN PRT NOUN DET NOUN ADP DET ADJ ADV VERB DET NOUN ADP DET NOUN').split()
hyp2 = ['PRON', 'VERB', 'PRT', 'VERB', 'DET', 'NOUN', 'ADV', 'VERB', 'DET', 'NOUN', 'NOUN', 'ADP', 'NOUN', 'VERB']
print('1 ', sentence_gleu([ref1], hyp1))
print('2', sentence_gleu([ref1], hyp2))

print('3 ', sentence_bleu([ref1], hyp1))
print('4 ', sentence_bleu([ref1], hyp2, weights=[1/3, 1/3, 1/3]))

print('5 ', sentence_chrf(ref1, hyp1))
print(sentence_chrf(ref1, hyp2))

print('6 ', sentence_nist([ref1], hyp1))
print('7 ', sentence_nist([ref1], hyp2))


