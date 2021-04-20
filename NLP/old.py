#
# def extract_subtrees(spacy_doc: Doc, sentence_tree: dict, subtrees_length: int) -> dict:
#     result = {1: [], 2: {}}
#
#     # 1-length
#     for token_info in spacy_doc.to_json()['tokens']:
#         result[1].append(token_info['id'])
#
#     # 2-level
#     if has_children(sentence_tree):
#         # extract root id
#         root_id = sentence_tree['id']
#         # extract children for that root
#         children = extract_children(list(sentence_tree.keys()))
#         # extract children ids
#         children_ids = []
#         for child in children:
#             children_ids.append(sentence_tree[child][0]['id'])
#
#         # result[2] = {
#         #     root_id: {
#         #         child_id: {} for child_id in children_ids
#         #     }
#         # }
#
#         result[2].update({
#             root_id: {
#                 child_id: {} for child_id in children_ids
#             }
#         })
#
#         while True:
#             # if any of the children have a child -> new 2-length should be added
#             for child in children:
#                 child_info = sentence_tree[child][0]
#                 if has_children(child_info):
#                     # extract root id
#                     root_id = child_info['id']
#                     # extract children for that root
#                     children_nested = extract_children(list(child_info.keys()))
#                     # extract children ids
#                     children_ids_nested = []
#                     for child_ in children_nested:
#                         children_ids_nested.append(child_info[child_][0]['id'])
#
#                     result[2].update({
#                         root_id: {
#                             child_id: {} for child_id in children_ids_nested
#                         }
#                     })
#             break
#
#     return result
#
#
# a = {}
#
#
# def extract_2_length_subtrees(tree: dict):
#     global a
#
#     if not has_children(tree):
#         return {}
#
#     # extract root id
#     root_id = tree['id']
#     # extract children for that root
#     children = extract_children(list(tree.keys()))
#     # extract children ids
#     children_ids = []
#     for child in children:
#         children_ids.append(tree[child][0]['id'])
#
#     a.update({
#         root_id: {
#             child_id: {} for child_id in children_ids
#         }
#     })
#
#     for child in children:
#         extract_2_length_subtrees(tree[child][0])
#
#
# def extract_3_length_subtrees(tree: dict):
#     if not has_children(tree):
#         return {}
#
#     # extract root id
#     root_id = tree['id']
#     # extract children for that root
#     children = extract_children(list(tree.keys()))
#     # extract children ids
#     children_ids = []
#     for child in children:
#         children_ids.append(tree[child][0]['id'])
#
#     # check that children (not) have children
#     for child in children:
#         # if have children
#         if has_children(tree[child][0]):
#             level_2_children = extract_children(tree[child][0])
#             level_2_children_ids = []
#             for child_ in level_2_children:
#                 level_2_children_ids.append(tree[child_][0]['id'])
#         else:
#             pass
#
#     # a.update({
#     #     root_id: {
#     #         child_id: {} for child_id in children_ids
#     #     }
#     # })
#
#     for child in children:
#         extract_2_length_subtrees(tree[child][0])
