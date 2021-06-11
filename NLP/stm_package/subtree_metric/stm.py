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

from typing import Union, Optional, Tuple, List, Dict

import spacy
from nltk import NaiveBayesClassifier
from sklearn.pipeline import Pipeline
from spacy import Language
from spacy.tokens import Token

from subtree_metric.classifier_utils import predict
from subtree_metric.tree_constructor import SyntaxTreeHeadsExtractor, SyntaxTreeElementsExtractor


def transform_into_tags(tokens: Tuple[Token]) -> tuple:
    """
    Return a tag collection for the given tokens.
    :param tokens: tokens for which to get tags
    :type tokens: tuple[Token]
    :return: a collection of tags
    :rtype: tuple
    """
    # TODO: align some tags: e.g. VBZ - VB
    return tuple([token.tag_ for token in tokens])


def get_freq_dict_for_tags(tags: tuple) -> dict:
    """
    Construct a frequency dictionary for the given tags
    :param tags:
    :type tags: tuple
    :return: a frequency dictionary
    :rtype: dict
    """
    result = {}
    for tag in tags:
        result[tag] = result.get(tag, 0) + 1
    return result


def are_descendants_identical(ref_extractor: SyntaxTreeElementsExtractor,
                              hyp_extractor: SyntaxTreeElementsExtractor) -> bool:
    """
    Check whether children of the given heads are identical
    :param ref_extractor: already filled in extractor (containing head -> children) for the reference
    :type ref_extractor: SyntaxTreeElementsExtractor
    :param hyp_extractor: already filled in extractor (containing head -> children) for the hypothesis
    :type hyp_extractor: SyntaxTreeElementsExtractor
    :return: whether children of these heads are identical
    :rtype: bool
    """
    ref_children_tags = transform_into_tags(ref_extractor.children)
    hyp_children_tags = transform_into_tags(hyp_extractor.children)

    ref_grandchildren_tags = transform_into_tags(ref_extractor.grand_children)
    hyp_grandchildren_tags = transform_into_tags(hyp_extractor.grand_children)

    are_children_identical = sorted(ref_children_tags) == sorted(hyp_children_tags)
    are_grandchildren_identical = sorted(ref_grandchildren_tags) == sorted(hyp_grandchildren_tags)

    return are_children_identical and are_grandchildren_identical


def sentence_stm(reference: str, hypothesis: str, nlp_model: Language, depth: int = 3) -> float:
    """
    Calculate sentence-level stm_package score.
        >>> hypothesis = 'It is a guide to action which ensures that the military always obeys the commands of the party'
        >>> reference = 'It is the guiding to action that ensures that the military will forever heed Party commands'
        >>> sentence_stm(reference, hypothesis, spacy_model, depth=3)
        0.4444
    :param reference: reference sentence
    :type reference: str
    :param hypothesis: hypothesis sentence
    :type hypothesis: str
    :param nlp_model: one of the SpaCy NLP models with support of the DependencyParser (https://spacy.io/models)
    :type nlp_model: Language
    :param depth: depth of the subtrees to take into account
    :type depth: int
    :return: stm score
    :rtype: float
    """
    score = 0.0
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


def sentence_stm_several_references(references: List[str],
                                    hypothesis: str,
                                    nlp_model: Language,
                                    depth: int = 3) -> float:
    """
    Calculate sentence-level stm_package score with several references vs. one hypothesis
    :param references: reference sentences
    :type references: List[str]
    :param hypothesis: hypothesis sentence
    :type hypothesis: str
    :param nlp_model: one of the SpaCy NLP models with support of the DependencyParser (https://spacy.io/models)
    :type nlp_model: Language
    :param depth: depth of the subtrees to take into account
    :type depth: int
    :return: stm_package score
    :rtype: float
    """
    nominator = 0
    denominator = len(references)
    for reference in references:
        nominator += sentence_stm(reference, hypothesis, nlp_model, depth)
    return round(nominator / denominator, 4)


def corpus_stm(references: List[str],
               hypotheses: List[str],
               nlp_model: Language,
               depth: int) -> float:
    """
    Calculate corpus-level stm_package score
    :param hypotheses: hypotheses
    :type hypotheses: list[str]
    :param references: references
    :type references: list[str]
    :param nlp_model: one of the SpaCy NLP models with support of the DependencyParser (https://spacy.io/models)
    :type nlp_model: Language
    :param depth: depth of the subtrees to take into account
    :type depth: int
    :return: Corpus stm_package score
    :rtype: float
    """
    # TODO: introduce sanity checks

    score = 0

    for reference_sentence, hypothesis_sentence in zip(references, hypotheses):
        score += sentence_stm(reference_sentence, hypothesis_sentence, nlp_model, depth)

    return round(score / len(references), 4)


def corpus_stm_augmented(references: List[str],
                         hypotheses: List[str],
                         nlp_model: Language,
                         sentiment_classifier: Optional[NaiveBayesClassifier] = None,
                         genre_classifier: Optional[Pipeline] = None,
                         depth: int = 3,
                         make_summary: bool = True) -> Union[float, Dict[str, Union[int, list]]]:
    """
    Calculate corpus-level stm_package score with additional weights from sentiment and genre classifiers - stm_package-Augmented
    :param hypotheses: hypotheses
    :type hypotheses: list[str]
    :param references: references
    :type references: list[str]
    :param nlp_model: one of the SpaCy NLP models with support of the DependencyParser (https://spacy.io/models)
    :type nlp_model: Language
    :param sentiment_classifier: a machine learning model that can predict the sentiment of the given sentence
    :type sentiment_classifier: NaiveBayesClassifier
    :param genre_classifier: a machine learning model that can predict the genre of the given sentence
    :type genre_classifier: Pipeline
    :param depth: depth of the subtrees to take into account
    :type depth: int
    :param make_summary: whether to make a per-sentence summary
    :type make_summary: bool
    :return: stm_package-A score
    :rtype: float
    """
    # TODO: introduce sanity checks
    score = 0

    per_sentence_summary: List[Dict[str, Union[str, float]]] = []

    idx = 0
    for reference_sentence, hypothesis_sentence in zip(references, hypotheses):
        sentence_score: float = sentence_stm(reference_sentence, hypothesis_sentence, nlp_model, depth)

        if sentiment_classifier or genre_classifier:
            sentence_score *= .7

        if make_summary:
            per_sentence_summary.append({
                'reference': reference_sentence,
                'hypothesis': hypothesis_sentence,
                'score': round(sentence_score, 4),
                'sentiment_ref': None,
                'sentiment_hyp': None,
                'genre_ref': None,
                'genre_hyp': None
            })

        if sentiment_classifier:
            sentiment_ref: str = predict(reference_sentence, sentiment_classifier)
            sentiment_hyp: str = predict(hypothesis_sentence, sentiment_classifier)

            sentence_score += 0.15 * int(sentiment_ref == sentiment_hyp) if genre_classifier else 0.3 * int(
                sentiment_ref == sentiment_hyp)

            if make_summary:
                per_sentence_summary[idx]['sentiment_ref'] = sentiment_ref
                per_sentence_summary[idx]['sentiment_hyp'] = sentiment_hyp
                per_sentence_summary[idx]['score'] = round(sentence_score, 4)

        if genre_classifier:
            genre_ref = genre_classifier.predict([reference_sentence])[0]
            genre_hyp = genre_classifier.predict([hypothesis_sentence])[0]

            sentence_score += 0.15 * int(genre_ref == genre_hyp) if sentiment_classifier else 0.3 * int(
                genre_ref == genre_hyp)

            if make_summary:
                per_sentence_summary[idx]['genre_ref'] = genre_ref
                per_sentence_summary[idx]['genre_hyp'] = genre_hyp
                per_sentence_summary[idx]['score'] = round(sentence_score, 4)

        score += sentence_score

        idx += 1

    genre_ref = None
    genre_hyp = None
    if genre_classifier:
        genre_ref = genre_classifier.predict(references)[0]
        genre_hyp = genre_classifier.predict(hypotheses)[0]

    if make_summary:
        return {'score': round(score / len(references), 4),
                'per_sentence_summary': per_sentence_summary,
                'genre': {'reference': genre_ref,
                          'hypothesis': genre_hyp}}

    return round(score / len(references), 4)


if __name__ == '__main__':
    # Usage example
    nlp: Language = spacy.load('en_core_web_md')
    ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
    hyp = 'It is a guide to action which ensures that the military always obeys the commands of the party'
    print(sentence_stm(ref,
                       hyp,
                       nlp))

    ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
    hyp = 'It is to insure the troops forever hearing the activity guidebook that party direct'
    print(sentence_stm(ref,
                       hyp,
                       nlp))
