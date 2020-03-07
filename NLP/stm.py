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
from nltk import Tree


def extract_pos(tree_dict: dict) -> dict:
    for subtree_len, subtrees in tree_dict.items():
        for index_subtree, subtree in enumerate(subtrees):
            posses = []
            for word_pos in subtree['leaves']:
                pos = word_pos.split('/')[1]
                posses.append(pos)
            tree_dict[subtree_len][index_subtree]['leaves'] = posses
    return tree_dict


def extract_subtrees(tree: Tree) -> dict:
    subtrees = list(tree.subtrees())[1:]  # Starting from '1' since the first one is the sentence itself.
    subtrees_dict = {}

    for subtree in subtrees:
        tree_dict = {'label': subtree.label(), 'leaves': subtree.leaves()}
        tree_len = len(tree_dict['leaves'])

        if not subtrees_dict.get(tree_len, 0):
            subtrees_dict[tree_len] = [tree_dict]
        else:
            subtrees_dict[tree_len].append(tree_dict)

    return extract_pos(subtrees_dict)


def count_subtree_in_tree(subtree: list, tree_dict: dict) -> int:
    subtree_len = len(subtree)
    count = 0
    for subtree_ in tree_dict[subtree_len]:
        if subtree == subtree_['leaves']:
            # print(subtree, tree_dict[subtree_len])
            count += 1

    return count


def stm(ref: Tree, hyp: Tree, depth: int = 2) -> [int, float]:
    ref_dict_tree = extract_subtrees(ref)
    hyp_dict_tree = extract_subtrees(hyp)

    count_ref = 0
    count_hyp = 0
    for i in range(1, depth + 1):
        all_subtrees_ref = ref_dict_tree[i]

        for subtree in all_subtrees_ref:
            ab = subtree['leaves']
            count_in_ref = count_subtree_in_tree(subtree['leaves'], ref_dict_tree)
            count_in_hyp = count_subtree_in_tree(subtree['leaves'], hyp_dict_tree)

            if count_in_hyp > count_in_ref:
                count_in_hyp = count_in_ref

            count_ref += count_in_ref
            count_hyp += count_in_hyp

            print(f'Leaf: {ab}, \n In ref: {count_in_ref}, \n In hyp: {count_in_hyp}')

    return (count_ref / count_hyp) / depth


a = Tree.fromstring('''(S
  (NP It/PRP)
  (VP be/VB)
  (NP a/DT guide/NN)
  (VP to/TO)
  (NP action/NN)
  (PP that/IN)
  (NP ensure/VB)
  (PP that/IN)
  (NP the/DT military/NN)
  (VP will/MD forever/VB heed/VB)
  (NP Party/NNP command/NN))''')
b = Tree.fromstring('''(S
  (NP It/PRP)
  (VP be/VB to/TO insure/VB)
  (NP the/DT troop/NN)
  forever/RB
  (VP hear/VBP)
  (NP the/DT activity/NN guidebook/NN)
  (NP that/WDT party/NN direct/NN))
''')
print(f'first: {a}')
print('*' * 10)
print(f'second: {b}')
print('*' * 20)
tree_dict_ = extract_subtrees(a)
print(tree_dict_)
print('*' * 30)
tree_dict_2 = extract_subtrees(b)
print(tree_dict_2)
print('*' * 30)
# print(count_subtree_in_tree(['VB', 'TO', 'VB'], tree_dict_2))
print(stm(b, a))

#
# '''
# 1 chunk_tree: $(S
#   (NP It/PRP)
#   (VP be/VB)
#   (NP a/DT guide/NN)
#   (VP to/TO)
#   (NP action/NN)
#   (PP that/IN)
#   (NP ensure/VB)
#   (PP that/IN)
#   (NP the/DT military/NN)
#   (VP will/MD forever/VB heed/VB)
#   (NP Party/NNP command/NN))
#   '''
#
# '''
# 2 chunk_tree: $(S
#   (NP It/PRP)
#   (VP be/VB to/TO insure/VB)
#   (NP the/DT troop/NN)
#   forever/RB
#   (VP hear/VBP)
#   (NP the/DT activity/NN guidebook/NN)
#   (NP that/WDT party/NN direct/NN))
# '''
#
# '''
# (S
#   (NP It/PRP)
#   (VP be/VB)
#   (NP a/DT guide/NN)
#   (VP to/TO)
#   (NP action/NN)
#   (NP which/WDT)
#   (VP ensure/VB)
#   (PP that/IN)
#   (NP the/DT military/JJ)
#   always/RB
#   (VP obey/VBP)
#   (NP the/DT command/NN)
#   (PP of/IN)
#   (NP the/DT party/NN))
# '''
