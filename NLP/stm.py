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
    pass


def sentence_stm(reference: str, hypothesis: str, model: Language):
    reference_preprocessed = model(reference)
    hypothesis_preprocessed = model(hypothesis)

    sentence_tree_heads_reference = SyntaxTreeHeadsExtractor(reference_preprocessed)
    sentence_tree_heads_hypothesis = SyntaxTreeHeadsExtractor(hypothesis_preprocessed)

    print(sentence_tree_heads_hypothesis.first_level_heads)
    print(sentence_tree_heads_reference.first_level_heads)
    print('*' * 100)
    print(sentence_tree_heads_hypothesis.second_level_heads)
    print(sentence_tree_heads_reference.second_level_heads)
    print('*' * 100)
    print(sentence_tree_heads_hypothesis.third_level_heads)
    print(sentence_tree_heads_reference.third_level_heads)
    print('*' * 100)
    tree_elements = SyntaxTreeElementsExtractor(sentence_tree_heads_hypothesis.third_level_heads[0])
    tree_elements_2 = SyntaxTreeElementsExtractor(sentence_tree_heads_reference.third_level_heads[0])
    print(tree_elements.children)
    print(tree_elements_2.children)
    print('*' * 100)
    print(tree_elements.grand_children)
    print(tree_elements_2.grand_children)

    # Compute for 1-level-trees
    transform_into_tags(sentence_tree_heads_hypothesis.first_level_heads)
    transform_into_tags(sentence_tree_heads_reference.first_level_heads)
    # Compute for 2-level-trees
    # Compute for 3-level-trees


nlp: Language = spacy.load('en_core_web_sm')
ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
hyp = 'It is a guide to action which ensures that the military always obeys the commands of the party'
sentence_stm(ref,
             hyp,
             nlp)
