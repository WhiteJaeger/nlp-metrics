from nltk.translate.bleu_score import corpus_bleu
from nltk.translate.meteor_score import meteor_score
from nltk.translate.nist_score import corpus_nist

from subtree_metric.stm import corpus_stm, corpus_stm_augmented
from main.models import GENRE_CLASSIFIER, SENTIMENT_CLASSIFIER, MODEL


def calculate_corpus_meteor(references_corpora: list[list[str]], hypotheses: list[str]) -> float:
    score = 0
    for references, hypothesis in zip(references_corpora, hypotheses):
        score += meteor_score(references, hypothesis)
    return score / len(references_corpora)


if __name__ == '__main__':
    # Read corpora
    with open('Autshumato.EvaluationSet.English.Translator1.txt', 'r', encoding='utf-8') as f:
        reference_corpora_1 = f.read().split('\n')

    with open('Autshumato.EvaluationSet.English.Translator2.txt', 'r', encoding='utf-8') as f:
        reference_corpora_2 = f.read().split('\n')

    with open('Autshumato.EvaluationSet.English.Translator3.txt', 'r', encoding='utf-8') as f:
        reference_corpora_3 = f.read().split('\n')

    with open('Autshumato.EvaluationSet.English.Translator4.txt', 'r', encoding='utf-8') as f:
        reference_corpora_4 = f.read().split('\n')

    # Transform corpora
    ## N-gram metrics digestible
    reference_corpora_1_for_ngram = [[sentence.split()] for sentence in reference_corpora_1][:500]
    hypothesis_corpora_1_for_ngram = [sentence.split() for sentence in reference_corpora_1][:500]

    reference_corpora_2_for_ngram = [[sentence.split()] for sentence in reference_corpora_2][:500]
    hypothesis_corpora_2_for_ngram = [sentence.split() for sentence in reference_corpora_2][:500]

    reference_corpora_3_for_ngram = [[sentence.split()] for sentence in reference_corpora_3][:500]
    hypothesis_corpora_3_for_ngram = [sentence.split() for sentence in reference_corpora_3][:500]

    reference_corpora_4_for_ngram = [[sentence.split()] for sentence in reference_corpora_4][:500]
    hypothesis_corpora_4_for_ngram = [sentence.split() for sentence in reference_corpora_4][:500]

    ## stm_package digestible
    reference_corpora_1_for_stm = reference_corpora_1[:500]
    reference_corpora_2_for_stm = reference_corpora_2[:500]
    reference_corpora_3_for_stm = reference_corpora_3[:500]
    reference_corpora_4_for_stm = reference_corpora_4[:500]

    ## METEOR digestible
    reference_corpora_1_meteor = [[sentence] for sentence in reference_corpora_1][:500]
    hypothesis_corpora_1_meteor = reference_corpora_1[:500]

    reference_corpora_2_meteor = [[sentence] for sentence in reference_corpora_2][:500]
    hypothesis_corpora_2_meteor = reference_corpora_2[:500]

    reference_corpora_3_meteor = [[sentence] for sentence in reference_corpora_3][:500]
    hypothesis_corpora_3_meteor = reference_corpora_3[:500]

    reference_corpora_4_meteor = [[sentence] for sentence in reference_corpora_4][:500]
    hypothesis_corpora_4_meteor = reference_corpora_4[:500]

    # Evaluation
    print('FIRST vs. FIRST')  # Sanity check that evaluation is done right and metrics are close to 1
    print(f'BLEU: {corpus_bleu(reference_corpora_1_for_ngram, hypothesis_corpora_1_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_1_for_ngram, hypothesis_corpora_1_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_1_meteor, hypothesis_corpora_1_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_1_for_stm, reference_corpora_1_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_1_for_stm, reference_corpora_1_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('SECOND vs. SECOND')  # Sanity check that evaluation is done right and metrics are close to 1
    print(f'BLEU: {corpus_bleu(reference_corpora_2_for_ngram, hypothesis_corpora_2_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_2_for_ngram, hypothesis_corpora_2_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_2_meteor, hypothesis_corpora_2_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_2_for_stm, reference_corpora_2_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_2_for_stm, reference_corpora_2_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('THIRD vs. THIRD')  # Sanity check that evaluation is done right and metrics are close to 1
    print(f'BLEU: {corpus_bleu(reference_corpora_3_for_ngram, hypothesis_corpora_3_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_3_for_ngram, hypothesis_corpora_3_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_3_meteor, hypothesis_corpora_3_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_3_for_stm, reference_corpora_3_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_3_for_stm, reference_corpora_3_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('FOURTH vs. FOURTH')  # Sanity check that evaluation is done right and metrics are close to 1
    print(f'BLEU: {corpus_bleu(reference_corpora_4_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_4_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_4_meteor, hypothesis_corpora_4_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_4_for_stm, reference_corpora_4_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_4_for_stm, reference_corpora_4_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('FIRST vs. SECOND')
    print(f'BLEU: {corpus_bleu(reference_corpora_1_for_ngram, hypothesis_corpora_2_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_1_for_ngram, hypothesis_corpora_2_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_1_meteor, hypothesis_corpora_2_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_1_for_stm, reference_corpora_2_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_1_for_stm, reference_corpora_2_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('FIRST vs. THIRD')
    print(f'BLEU: {corpus_bleu(reference_corpora_1_for_ngram, hypothesis_corpora_3_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_1_for_ngram, hypothesis_corpora_3_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_1_meteor, hypothesis_corpora_3_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_1_for_stm, reference_corpora_3_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_1_for_stm, reference_corpora_3_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('FIRST vs. FOURTH')
    print(f'BLEU: {corpus_bleu(reference_corpora_1_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_1_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_1_meteor, hypothesis_corpora_4_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_1_for_stm, reference_corpora_4_for_stm, MODEL, 3)}')
    results = corpus_stm_augmented(reference_corpora_1_for_stm, reference_corpora_4_for_stm, MODEL,
                                   SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, True)
    print(sorted(results['per_sentence_summary'], key=lambda summary: summary['score'])[:10])
    print(
        f'STM-A: {results["score"]}')

    print('*' * 100)
    print('SECOND vs. THIRD')
    print(f'BLEU: {corpus_bleu(reference_corpora_2_for_ngram, hypothesis_corpora_3_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_2_for_ngram, hypothesis_corpora_3_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_2_meteor, hypothesis_corpora_3_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_2_for_stm, reference_corpora_3_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_2_for_stm, reference_corpora_3_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('SECOND vs. FOURTH')
    print(f'BLEU: {corpus_bleu(reference_corpora_2_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_2_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_2_meteor, hypothesis_corpora_4_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_2_for_stm, reference_corpora_4_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_2_for_stm, reference_corpora_4_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('THIRD vs. FOURTH')
    print(f'BLEU: {corpus_bleu(reference_corpora_3_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'NIST: {corpus_nist(reference_corpora_3_for_ngram, hypothesis_corpora_4_for_ngram)}')
    print(f'METEOR: {calculate_corpus_meteor(reference_corpora_3_meteor, hypothesis_corpora_4_meteor)}')
    print(f'STM: {corpus_stm(reference_corpora_3_for_stm, reference_corpora_4_for_stm, MODEL, 3)}')
    print(
        f'STM-A: {corpus_stm_augmented(reference_corpora_3_for_stm, reference_corpora_4_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 3, False)}')

    print('*' * 100)
    print('THIRD vs. FOURTH')
    print(f'STM 1-length trees: {corpus_stm(reference_corpora_3_for_stm, reference_corpora_4_for_stm, MODEL, 1)}')
    print(
        f'STM-A 1-length trees: {corpus_stm_augmented(reference_corpora_3_for_stm, reference_corpora_4_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 1, False)}')

    print(f'STM 2-length trees: {corpus_stm(reference_corpora_3_for_stm, reference_corpora_4_for_stm, MODEL, 2)}')
    print(
        f'STM-A 2-length trees: {corpus_stm_augmented(reference_corpora_3_for_stm, reference_corpora_4_for_stm, MODEL, SENTIMENT_CLASSIFIER, GENRE_CLASSIFIER, 2, False)}')

# Results
# FIRST vs. FIRST
# BLEU: 0.9982658457109393
# NIST: 13.368063436646528
# METEOR: 0.990656415293831
# stm_package: 0.978
# stm_package-A: 0.9846
# ****************************************************************************************************
# FIRST vs. SECOND
# BLEU: 0.3131650301477595
# NIST: 6.842192206781902
# METEOR: 0.619288750881706
# stm_package: 0.5471
# stm_package-A: 0.6272
# ****************************************************************************************************
# FIRST vs. THIRD
# BLEU: 0.24805461218182004
# NIST: 5.8718347913668145
# METEOR: 0.559153052520805
# stm_package: 0.5002
# stm_package-A: 0.5778
# ****************************************************************************************************
# FIRST vs. FOURTH
# BLEU: 0.5076389102316189
# NIST: 9.22117726382084
# METEOR: 0.7857194322505343
# stm_package: 0.6836
# stm_package-A: 0.7395
# ****************************************************************************************************
# SECOND vs. THIRD
# BLEU: 0.23689570084576927
# NIST: 5.694706837152382
# METEOR: 0.5329311830287575
# stm_package: 0.5001
# stm_package-A: 0.5748
# ****************************************************************************************************
# SECOND vs. FOURTH
# BLEU: 0.37067794028495965
# NIST: 7.656434932184833
# METEOR: 0.650511115690221
# stm_package: 0.5832
# stm_package-A: 0.6545
# ****************************************************************************************************
# THIRD vs. FOURTH
# BLEU: 0.2665348537463917
# NIST: 6.439588648675369
# METEOR: 0.5534725866134054
# stm_package: 0.5385
# stm_package-A: 0.607
