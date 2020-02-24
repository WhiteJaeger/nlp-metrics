"""
Subtree evaluation metric as described in 'Syntactic Features for Evaluation of Machine Translation' by
Ding Liu and Daniel Gildea, 2005, Association for Computational Linguistics, Pages: 25–32
@inproceedings{liu-gildea-2005-syntactic,
    title = "Syntactic Features for Evaluation of Machine Translation",
    author = "Liu, Ding  and
      Gildea, Daniel",
    booktitle = "Proceedings of the {ACL} Workshop on Intrinsic and Extrinsic Evaluation Measures for Machine Translation and/or Summarization",
    month = jun,
    year = "2005",
    address = "Ann Arbor, Michigan",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W05-0904",
    pages = "25--32",
}
"""
from nltk import Tree


class STM:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.ref_tree = None
        self.hyp_tree = None

    def calculate_stm(self, ref_tree: Tree, hyp_tree: Tree):
        pass

    @staticmethod
    def _extract_subtrees(sentence_tree: Tree) -> dict:
        subtrees = list(sentence_tree.subtrees())[1:]  # Starting from '1' since the first one is the sentence itself.
        subtrees_dict = {}

        for tree in subtrees:
            tree_dict = {'label': tree.label(), 'leaves': tree.leaves()}
            tree_len = len(tree_dict['leaves'])

            if not subtrees_dict.get(tree_len, 0):
                subtrees_dict[tree_len] = [tree_dict]
            else:
                subtrees_dict[tree_len].append(tree_dict)

        return subtrees_dict

    def store_subtrees(self, ref_tree: Tree, hyp_tree: Tree):
        self.ref_tree = self._extract_subtrees(ref_tree)
        self.hyp_tree = self._extract_subtrees(hyp_tree)

    def _count_subtrees_present_in_hyp(self, subtrees_len: int) -> int:
        return len(self.hyp_tree[subtrees_len])

    def _count_subtrees_present_in_ref(self, subtrees_len: int) -> int:
        subtrees_ref = self.ref_tree[subtrees_len]
        subtrees_hyp = self.hyp_tree[subtrees_len]

        counter = 0
        for subtree in subtrees_ref:
            if subtree in subtrees_hyp:
                counter += 1
        return counter

    def extract_pos(self):
        for subtrees_len, subtrees in self.hyp_tree.items():
            for index_subtree, subtree in enumerate(subtrees):
                pos_leaves = []
                for word_pos in subtree['leaves']:
                    pos = word_pos.split('/')[1]
                    pos_leaves.append(pos)
                self.hyp_tree[subtrees_len][index_subtree]['leaves'] = pos_leaves

        for subtrees_len, subtrees in self.ref_tree.items():
            for index_subtree, subtree in enumerate(subtrees):
                pos_leaves = []
                for word_pos in subtree['leaves']:
                    pos = word_pos.split('/')[1]
                    pos_leaves.append(pos)
                self.ref_tree[subtrees_len][index_subtree]['leaves'] = pos_leaves

    def count_similar_subtrees(self, depth):
        counter = 0
        leaves_hyp = self.extract_leaves(self.hyp_tree[depth])
        leaves_ref = self.extract_leaves(self.ref_tree[depth])
        for leave in leaves_hyp:
            if leave in leaves_ref:
                counter += 1

        print(f'HYP: {leaves_hyp}, \n REF: {leaves_ref}')
        return counter

    def extract_leaves(self, subtree: list):
        leaves = []
        for tree in subtree:
            leaves.append(tree['leaves'])
        return leaves


ex = STM()
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
print('*' * 20)
ex.store_subtrees(a, b)
ex.extract_pos()
print(ex.count_similar_subtrees(2))

'''
1 chunk_tree: $(S
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
  (NP Party/NNP command/NN))
  '''

'''
2 chunk_tree: $(S
  (NP It/PRP)
  (VP be/VB to/TO insure/VB)
  (NP the/DT troop/NN)
  forever/RB
  (VP hear/VBP)
  (NP the/DT activity/NN guidebook/NN)
  (NP that/WDT party/NN direct/NN))
'''

'''
(S
  (NP It/PRP)
  (VP be/VB)
  (NP a/DT guide/NN)
  (VP to/TO)
  (NP action/NN)
  (NP which/WDT)
  (VP ensure/VB)
  (PP that/IN)
  (NP the/DT military/JJ)
  always/RB
  (VP obey/VBP)
  (NP the/DT command/NN)
  (PP of/IN)
  (NP the/DT party/NN))
'''
