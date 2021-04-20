import spacy
from spacy.tokens import Doc
from spacy.tokens import Token
from nltk import Tree
from pprint import pprint

from NLP.tree_transformer import tree_to_dict

nlp = spacy.load('en_core_web_sm')
# doc: Doc = nlp(u'i have a red pen')
doc: Doc = nlp(u'Diplomatic staff would go home in a fifth plane')

doc_tree = list(tree_to_dict(doc.to_json(), ['end', 'start', 'pos', 'dep', 'morph', 'lemma']))[0]
pprint(doc_tree)
print('*' * 100)


def has_children(token_info: dict) -> bool:
    constant_attrs = ['head', 'id', 'tag', 'text']

    return len([key for key in token_info.keys() if key not in constant_attrs]) > 0


def extract_children(token_info: list) -> list:
    constant_attrs = ['head', 'id', 'tag', 'text']

    return [key for key in token_info if key not in constant_attrs]


print(f'FROM TOP LEVEL: {extract_children(doc_tree)}')
print(f'FROM ONE OF THE CHILDREN [prep]: {extract_children(doc_tree["prep"])}')
print('*' * 100)


# a = list()
# def myprint(d):
#     for k, v in d.items():
#         if isinstance(v, dict):
#             a.append(v)
#             myprint(v)
#         else:
#             # print("{0}: {1}".format(k, v))
#             pass


# myprint(doc_tree['prep'])
# print(a)

print('*' * 100)
