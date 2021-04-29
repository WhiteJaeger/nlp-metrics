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
import spacy
from spacy import Language
from spacy.tokens import Token

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


def sentence_stm(reference: str, hypothesis: str, model: Language, depth: int = 3) -> float:
    """

    :param reference:
    :type reference:
    :param hypothesis:
    :type hypothesis:
    :param model:
    :type model:
    :param depth:
    :type depth:
    :return:
    :rtype:
    """
    score = 0
    # Get output from SpaCy model
    reference_preprocessed = model(reference)
    hypothesis_preprocessed = model(hypothesis)

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
                                    model: Language,
                                    depth: int = 3) -> float:
    """

    :param references:
    :type references:
    :param hypothesis:
    :type hypothesis:
    :param model:
    :type model:
    :param depth:
    :type depth:
    :return:
    :rtype:
    """
    nominator = 0
    denominator = len(references)
    for reference in references:
        nominator += sentence_stm(reference, hypothesis, model, depth)
    return round(nominator / denominator, 4)


def corpus_stm(references: list[list[str]],
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
    nlp: Language = spacy.load('en_core_web_sm')
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
