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

from NLP.tree_constructor import SyntaxTreeHeadsExtractor, SyntaxTreeElementsExtractor


def transform_into_tags(tokens: tuple) -> tuple:
    # TODO: align some tags: e.g. VBZ - VB
    return tuple([token.tag_ for token in tokens])


def get_freq_dict_for_tags(tags: tuple) -> dict:
    result = {}
    for tag in tags:
        result[tag] = result.get(tag, 0) + 1
    return result


def are_descendants_identical(ref_extractor: SyntaxTreeElementsExtractor, hyp_extractor: SyntaxTreeElementsExtractor):
    ref_children_tags = transform_into_tags(ref_extractor.children)
    hyp_children_tags = transform_into_tags(hyp_extractor.children)

    ref_grandchildren_tags = transform_into_tags(ref_extractor.grand_children)
    hyp_grandchildren_tags = transform_into_tags(hyp_extractor.grand_children)

    are_children_identical = sorted(ref_children_tags) == sorted(hyp_children_tags)
    are_grandchildren_identical = sorted(ref_grandchildren_tags) == sorted(hyp_grandchildren_tags)

    return are_children_identical and are_grandchildren_identical


def sentence_stm(reference: str, hypothesis: str, model: Language, depth: int = 3):
    # TODO: introduce depth argument
    # TODO: remove 'prints'
    score = 0
    reference_preprocessed = model(reference)
    hypothesis_preprocessed = model(hypothesis)

    sentence_tree_heads_reference = SyntaxTreeHeadsExtractor(reference_preprocessed)
    sentence_tree_heads_hypothesis = SyntaxTreeHeadsExtractor(hypothesis_preprocessed)
    # print('FIRST LEVEL HEADS:')
    # print(sentence_tree_heads_hypothesis.first_level_heads)
    # print(sentence_tree_heads_reference.first_level_heads)
    # print('*' * 100)
    # print('SECOND LEVEL HEADS:')
    # print(sentence_tree_heads_hypothesis.second_level_heads)
    # print(sentence_tree_heads_reference.second_level_heads)
    # print('*' * 100)
    # print('THIRD LEVEL HEADS:')
    # print(sentence_tree_heads_hypothesis.third_level_heads)
    # print(sentence_tree_heads_reference.third_level_heads)
    # print('*' * 100)
    # tree_elements = SyntaxTreeElementsExtractor(sentence_tree_heads_hypothesis.third_level_heads[0])
    # tree_elements_2 = SyntaxTreeElementsExtractor(sentence_tree_heads_reference.third_level_heads[0])
    # print(tree_elements.children)
    # print(tree_elements_2.children)
    # print('*' * 100)
    # print(tree_elements.grand_children)
    # print(tree_elements_2.grand_children)

    # Compute for 1-level-trees
    # print('*' * 100)
    # print('FIRST LEVEL:')
    tags_first_level_ref = transform_into_tags(sentence_tree_heads_reference.first_level_heads)
    tags_first_level_hyp = transform_into_tags(sentence_tree_heads_hypothesis.first_level_heads)
    # print(tags_first_level_ref)
    # print(tags_first_level_hyp)

    tags_frequencies_ref = get_freq_dict_for_tags(transform_into_tags(sentence_tree_heads_reference.first_level_heads))
    tags_frequencies_hyp = get_freq_dict_for_tags(transform_into_tags(sentence_tree_heads_hypothesis.first_level_heads))

    # print(tags_frequencies_ref)
    # print(tags_frequencies_hyp)
    count = 0
    for tag in tags_frequencies_hyp:
        # Get already clipped value - number of times a tag appears in reference
        count += tags_frequencies_ref.get(tag, 0)
    result = count / len(tags_first_level_hyp)
    # print(result)
    score += result
    # Compute for 2-level-trees
    # print('*' * 100)
    # print('TWO LEVEL:')
    # print(sentence_tree_heads_reference.second_level_heads[0])
    # print(sentence_tree_heads_hypothesis.second_level_heads[0])
    # el_ref = SyntaxTreeElementsExtractor(sentence_tree_heads_reference.second_level_heads[0])
    # el_hyp = SyntaxTreeElementsExtractor(sentence_tree_heads_hypothesis.second_level_heads[0])
    # print(el_ref.children)
    # print(el_hyp.children)

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
    # print(count)
    # print(count / len(sentence_tree_heads_hypothesis.second_level_heads))
    score += count / len(sentence_tree_heads_hypothesis.second_level_heads)
    #############################################################################
    # Compute for 3-level-trees
    # print('*' * 100)
    # print('THIRD LEVEL:')
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
                # else:
                #     print('|' * 100)
                #     print(third_level_head_hyp)
                #     print(extractor_hyp.children)
                #     print(transform_into_tags(extractor_hyp.children))
                #     print(extractor_hyp.grand_children)
                #     print(transform_into_tags(extractor_hyp.grand_children))
                #     print()
                #     print(third_level_head_ref)
                #     print(extractor_ref.children)
                #     print(transform_into_tags(extractor_ref.children))
                #     print(extractor_ref.grand_children)
                #     print(transform_into_tags(extractor_ref.grand_children))
                #     print('|' * 100)
    # print(count)
    # print(count / len(third_level_hyp))
    score += count / len(third_level_hyp)
    return round(score / depth, 4)


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
