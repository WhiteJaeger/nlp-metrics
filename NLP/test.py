import rouge
from nltk.translate.gleu_score import sentence_gleu, corpus_gleu
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
from nltk.translate.chrf_score import sentence_chrf, corpus_chrf
from nltk.translate.nist_score import sentence_nist, corpus_nist
from nltk.translate.meteor_score import single_meteor_score, meteor_score

ref1 = str('It is a guide to action that ensures that the military will forever heed Party commands').split()
hyp1 = str('It is a guide to action which ensures that the military always obeys the commands of the party').split()
hyp2 = str('It is to insure the troops forever hearing the activity guidebook that party direct').split()
print(sentence_gleu([ref1], hyp1))
print(sentence_gleu([ref1], hyp2))

print(sentence_bleu([ref1], hyp1))
# print(sentence_bleu([ref1], hyp2))

print(sentence_chrf(ref1, hyp1))
print(sentence_chrf(ref1, hyp2))

print(sentence_nist([ref1], hyp1))
print(sentence_nist([ref1], hyp2))


