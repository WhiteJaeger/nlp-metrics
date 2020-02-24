# from abc import ABC
#
# import nltk
#
# from NLP.text_utils import prepare_text
#
# sentence = str('I am a student in the HSE university')
#
# # POS tagging with nltk
# nltk_pos_tagged = nltk.pos_tag(sentence.split())
#
# print(nltk_pos_tagged)
#
# from nltk.corpus import conll2000
#
# data = conll2000.chunked_sents()
# train_data = data[:5450]
# test_data = data[5450:]
#
# print(len(train_data), len(test_data))
# print(train_data[1])
# from nltk.chunk.util import tree2conlltags, conlltags2tree
#
# wtc = tree2conlltags(train_data[1])
#
#
# def conll_tag_chunks(chunk_sents):
#     tagged_sents = [tree2conlltags(tree) for tree in chunk_sents]
#     return [[(t, c) for (w, t, c) in sent] for sent in tagged_sents]
#
#
# def combined_tagger(train_data, taggers, backoff=None):
#     for tagger in taggers:
#         backoff = tagger(train_data, backoff=backoff)
#     return backoff
#
#
# from nltk.tag import UnigramTagger, BigramTagger
# from nltk.chunk import ChunkParserI
#
#
# # define the chunker class
# class NGramTagChunker(ChunkParserI, ABC):
#
#     def __init__(self, train_sentences,
#                  tagger_classes=(UnigramTagger, BigramTagger)):
#         train_sent_tags = conll_tag_chunks(train_sentences)
#         self.chunk_tagger = combined_tagger(train_sent_tags, tagger_classes)
#
#     def parse(self, tagged_sentence):
#         if not tagged_sentence:
#             return None
#         pos_tags = [tag for word, tag in tagged_sentence]
#         chunk_pos_tags = self.chunk_tagger.tag(pos_tags)
#         chunk_tags = [chunk_tag for (pos_tag, chunk_tag) in chunk_pos_tags]
#         wpc_tags = [(word, pos_tag, chunk_tag) for ((word, pos_tag), chunk_tag)
#                     in zip(tagged_sentence, chunk_tags)]
#         return conlltags2tree(wpc_tags)
#
#
# # train chunker model
# ntc = NGramTagChunker(train_data)
#
# # evaluate chunker model performance
# print(ntc.evaluate(test_data))
#
# sentence = 'It is a guide to action that ensures that the military will forever heed Party commands'
# sentence = prepare_text(sentence, text_lower_case=False, stopword_removal=False)
#
# sentence_2 = 'It is a guide to action which ensures that the military always obeys the commands of the party'
# sentence_2 = prepare_text(sentence_2, text_lower_case=False, stopword_removal=False)
#
# nltk_pos_tagged_1 = nltk.pos_tag(sentence.split())
# nltk_pos_tagged_2 = nltk.pos_tag(sentence_2.split())
#
# print(f'1 sentence: ${nltk_pos_tagged_1}')
# print(f'2 sentence: ${nltk_pos_tagged_2}')
# print('*' * 20)
#
# chunk_tree_1 = ntc.parse(nltk_pos_tagged_1)
# print(f'1 chunk_tree: ${chunk_tree_1}')
# print(list(chunk_tree_1.subtrees()))
# print('*' * 20)
# chunk_tree_2 = ntc.parse(nltk_pos_tagged_2)
# print(f'2 chunk_tree: ${chunk_tree_2}')
# print(list(chunk_tree_2.subtrees()))
