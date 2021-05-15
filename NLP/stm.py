"""
Subtree evaluation metric as described in 'Syntactic Features for Evaluation of Machine Translation' by
Ding Liu and Daniel Gildea, 2005, Association for Computational Linguistics, Pages: 25–32
@inproceedings{liu-gildea-2005-syntactic,
    title = "Syntactic Features for Evaluation of Machine Translation",
    author = "Liu, Ding  and
      Gildea, Daniel",
    booktitle = "Proceedings of the {ACL} Workshop on Intrinsic and Extrinsic Evaluation Measures for Machine
    Translation and/or Summarization",
    month = jun,
    year = "2005",
    address = "Ann Arbor, Michigan",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W05-0904",
    pages = "25--32",
}
"""
from typing import Union, Optional

import spacy
from nltk import NaiveBayesClassifier
from sklearn.pipeline import Pipeline
from spacy import Language
from spacy.tokens import Token

from NLP.classifier_utils import predict
from NLP.tree_constructor import SyntaxTreeHeadsExtractor, SyntaxTreeElementsExtractor


def transform_into_tags(tokens: tuple[Token]) -> tuple:
    # TODO: align some tags: e.g. VBZ - VB
    return tuple([token.tag_ for token in tokens])


def get_freq_dict_for_tags(tags: tuple) -> dict:
    result = {}
    for tag in tags:
        result[tag] = result.get(tag, 0) + 1
    return result


def are_descendants_identical(ref_extractor: SyntaxTreeElementsExtractor,
                              hyp_extractor: SyntaxTreeElementsExtractor) -> bool:
    ref_children_tags = transform_into_tags(ref_extractor.children)
    hyp_children_tags = transform_into_tags(hyp_extractor.children)

    ref_grandchildren_tags = transform_into_tags(ref_extractor.grand_children)
    hyp_grandchildren_tags = transform_into_tags(hyp_extractor.grand_children)

    are_children_identical = sorted(ref_children_tags) == sorted(hyp_children_tags)
    are_grandchildren_identical = sorted(ref_grandchildren_tags) == sorted(hyp_grandchildren_tags)

    return are_children_identical and are_grandchildren_identical


def sentence_stm(reference: str, hypothesis: str, nlp_model: Language, depth: int = 3) -> float:
    """

    :param reference:
    :type reference:
    :param hypothesis:
    :type hypothesis:
    :param nlp_model:
    :type nlp_model:
    :param depth:
    :type depth:
    :return:
    :rtype:
    """
    score = 0
    # Get output from SpaCy model
    reference_preprocessed = nlp_model(reference)
    hypothesis_preprocessed = nlp_model(hypothesis)

    # Get heads of syntax trees
    sentence_tree_heads_reference = SyntaxTreeHeadsExtractor(reference_preprocessed)
    sentence_tree_heads_hypothesis = SyntaxTreeHeadsExtractor(hypothesis_preprocessed)

    tags_first_level_hyp = transform_into_tags(sentence_tree_heads_hypothesis.first_level_heads)

    # Get frequencies of individual tags
    tags_frequencies_ref = get_freq_dict_for_tags(transform_into_tags(sentence_tree_heads_reference.first_level_heads))
    tags_frequencies_hyp = get_freq_dict_for_tags(transform_into_tags(sentence_tree_heads_hypothesis.first_level_heads))

    # Compute for 1-level-trees, i.e. individual tags
    count = 0
    for tag in tags_frequencies_hyp:
        # Get already clipped value - number of times a tag appears in reference
        count += tags_frequencies_ref.get(tag, 0)
    score += count / len(tags_first_level_hyp) if len(tags_first_level_hyp) else 0

    if depth >= 2:
        # Compute for 2-level-trees
        used_heads_indexes = []
        count = 0
        for two_level_head_hyp in sentence_tree_heads_hypothesis.second_level_heads:
            for idx, two_level_head_ref in enumerate(sentence_tree_heads_reference.second_level_heads):
                if idx in used_heads_indexes:
                    continue
                if two_level_head_hyp.tag_ == two_level_head_ref.tag_:
                    # Get children
                    ref_children_tags = transform_into_tags(SyntaxTreeElementsExtractor(two_level_head_ref).children)
                    hyp_children_tags = transform_into_tags(SyntaxTreeElementsExtractor(two_level_head_hyp).children)
                    # Check if their children are identical
                    if sorted(ref_children_tags) == sorted(hyp_children_tags):
                        count += 1
                        used_heads_indexes.append(idx)
        score += count / len(sentence_tree_heads_hypothesis.second_level_heads) \
            if len(sentence_tree_heads_hypothesis.second_level_heads) else 0

    if depth >= 3:
        # Compute for 3-level-trees
        count = 0
        third_level_hyp = sentence_tree_heads_hypothesis.third_level_heads
        third_level_ref = sentence_tree_heads_reference.third_level_heads
        used_heads_indexes = []
        for third_level_head_hyp in third_level_hyp:
            # Same as in 2-level
            for idx, third_level_head_ref in enumerate(third_level_ref):
                if idx in used_heads_indexes:
                    continue
                if third_level_head_hyp.tag_ == third_level_head_ref.tag_:
                    # Get children & grandchildren
                    extractor_ref = SyntaxTreeElementsExtractor(third_level_head_ref)
                    extractor_hyp = SyntaxTreeElementsExtractor(third_level_head_hyp)
                    # Check if their children & grandchildren are identical
                    if are_descendants_identical(extractor_ref, extractor_hyp):
                        count += 1
                        used_heads_indexes.append(idx)

        score += count / len(third_level_hyp) if len(third_level_hyp) else 0

    return round(score / depth, 4)


def sentence_stm_several_references(references: list[str],
                                    hypothesis: str,
                                    nlp_model: Language,
                                    depth: int = 3) -> float:
    """

    :param references:
    :type references:
    :param hypothesis:
    :type hypothesis:
    :param nlp_model:
    :type nlp_model:
    :param depth:
    :type depth:
    :return:
    :rtype:
    """
    nominator = 0
    denominator = len(references)
    for reference in references:
        nominator += sentence_stm(reference, hypothesis, nlp_model, depth)
    return round(nominator / denominator, 4)


def corpus_stm(corpora: dict[str, list[str]],
               nlp_model: Language,
               depth: int) -> float:
    """

    :param corpora:
    :type corpora:
    :param nlp_model:
    :type nlp_model:
    :param depth:
    :type depth:
    :return:
    :rtype:
    """
    score = 0

    for reference_sentence, hypothesis_sentence in zip(corpora['references'], corpora['hypotheses']):
        score += sentence_stm(reference_sentence, hypothesis_sentence, nlp_model, depth)

    return round(score / len(corpora['references']), 4)


def corpus_stm_augmented(corpora: dict[str, list[str]],
                         nlp_model: Language,
                         sentiment_classifier: Optional[NaiveBayesClassifier] = None,
                         genre_classifier: Optional[Pipeline] = None,
                         depth: int = 3,
                         make_summary: bool = True) -> Union[float, dict[str, Union[int, list]]]:
    """

    :param corpora:
    :type corpora:
    :param nlp_model:
    :type nlp_model:
    :param sentiment_classifier:
    :type sentiment_classifier:
    :param genre_classifier:
    :type genre_classifier:
    :param depth:
    :type depth:
    :param make_summary:
    :type make_summary:
    :return:
    :rtype:
    """
    score = 0

    per_sentence_summary: list[dict[str, Union[str, float]]] = []

    idx = 0
    for reference_sentence, hypothesis_sentence in zip(corpora['references'], corpora['hypotheses']):
        sentence_score: float = round(sentence_stm(reference_sentence, hypothesis_sentence, nlp_model, depth), 4)

        if make_summary:
            per_sentence_summary.append({
                'reference': reference_sentence,
                'hypothesis': hypothesis_sentence,
                'score': sentence_score,
                'sentiment_ref': None,
                'sentiment_hyp': None,
                'genre_ref': None,
                'genre_hyp': None
            })

        if sentiment_classifier:
            sentiment_ref: str = predict(reference_sentence, sentiment_classifier)
            sentiment_hyp: str = predict(hypothesis_sentence, sentiment_classifier)
            sentence_score += 0.5 * int(sentiment_ref == sentiment_hyp)

            if make_summary:
                per_sentence_summary[idx]['sentiment_ref'] = sentiment_ref
                per_sentence_summary[idx]['sentiment_hyp'] = sentiment_hyp
                per_sentence_summary[idx]['score'] = sentence_score

        if genre_classifier:
            genre_ref = genre_classifier.predict([reference_sentence])[0]
            genre_hyp = genre_classifier.predict([hypothesis_sentence])[0]
            sentence_score += 0.5 * int(genre_ref == genre_hyp)

            if make_summary:
                per_sentence_summary[idx]['genre_ref'] = genre_ref
                per_sentence_summary[idx]['genre_hyp'] = genre_hyp
                per_sentence_summary[idx]['score'] = sentence_score

        score += sentence_score

        idx += 1

    genre_ref = None
    genre_hyp = None
    if genre_classifier:
        genre_ref = genre_classifier.predict(corpora['references'])[0]
        genre_hyp = genre_classifier.predict(corpora['hypotheses'])[0]

    if make_summary:
        return {'score': round(score / len(corpora['references']), 4),
                'per_sentence_summary': per_sentence_summary,
                'genre': {'reference': genre_ref,
                          'hypothesis': genre_hyp}}

    return round(score / len(corpora['references']), 4)


def corpus_stm_several_references(references: list[list[str]],
                                  hypotheses: list[str],
                                  model: Language,
                                  depth: int = 3) -> float:
    """

    :param references:
    :type references:
    :param hypotheses:
    :type hypotheses:
    :param model:
    :type model:
    :param depth:
    :type depth:
    :return:
    :rtype:
    """
    if len(references) != len(hypotheses):
        # TODO: error-handling
        raise AssertionError

    # There can be several references for one hypothesis
    nominator = 0
    denominator = len(references)
    for refs, hypothesis in zip(references, hypotheses):
        nominator += sentence_stm_several_references(refs, hypothesis, model, depth)
    return round(nominator / denominator, 4)


if __name__ == '__main__':
    # Usage example
    nlp: Language = spacy.load('en_core_web_md')
    ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
    hyp = 'It is a guide to action which ensures that the military always obeys the commands of the party'
    sentence_stm(ref,
                 hyp,
                 nlp)

    ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
    hyp = 'It is to insure the troops forever hearing the activity guidebook that party direct'
    sentence_stm(ref,
                 hyp,
                 nlp)
