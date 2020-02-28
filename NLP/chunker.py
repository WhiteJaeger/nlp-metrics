import pathlib
from abc import ABC
from os import path

from joblib import load
from nltk.chunk import ChunkParserI
from nltk.chunk.util import tree2conlltags, conlltags2tree
from nltk.corpus import conll2000
from nltk.tag import UnigramTagger, BigramTagger

from NLP.text_utils import prepare_str

data = list(conll2000.chunked_sents())
print(len(data))
train_data = data[:5450]
test_data = data[5450:]

# print(len(train_data), len(test_data))
print(train_data[1])
#
wtc = tree2conlltags(train_data[1])
print(wtc)


def conll_tag_chunks(chunk_sents):
    tagged_sents = [tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in sent] for sent in tagged_sents]


def combined_tagger(train_data, taggers, backoff=None):
    for tagger in taggers:
        backoff = tagger(train_data, backoff=backoff)
    return backoff


#
#
# define the chunker class
class NGramTagChunker(ChunkParserI, ABC):

    def __init__(self, train_sentences,
                 tagger_classes=(UnigramTagger, BigramTagger)):
        train_sent_tags = conll_tag_chunks(train_sentences)
        self.chunk_tagger = combined_tagger(train_sent_tags, tagger_classes)

    def parse(self, tagged_sentence):
        if not tagged_sentence:
            return None
        pos_tags = [tag for word, tag in tagged_sentence]
        chunk_pos_tags = self.chunk_tagger.tag(pos_tags)
        chunk_tags = [chunk_tag for (pos_tag, chunk_tag) in chunk_pos_tags]
        wpc_tags = [(word, pos_tag, chunk_tag) for ((word, pos_tag), chunk_tag)
                    in zip(tagged_sentence, chunk_tags)]
        return conlltags2tree(wpc_tags)


#
# train chunker model
ntc = NGramTagChunker(train_data)
#
# evaluate chunker model performance
print(ntc.evaluate(test_data))


# Testing predictions
sentence = 'It is a guide to action that ensures that the military will forever heed Party commands'
sentence_prepared = prepare_str(sentence, text_lower_case=False, stopword_removal=False, pos_preparation=True)
#
sentence_2 = 'It is a guide to action which ensures that the military always obeys the commands of the party'
sentence_2_prepared = prepare_str(sentence_2, text_lower_case=False, stopword_removal=False, pos_preparation=True)

project_path = str(pathlib.Path(__file__).parents[1])
model_path = path.join(project_path, 'models', 'crfWJSModel900k.joblib')
crf = load(model_path)
#
pos_tagged_1 = crf.predict(sentence_prepared)[0]
pos_tagged_2 = crf.predict(sentence_2_prepared)[0]
#
print(f'1 sentence tagged: {pos_tagged_1}')
print(f'2 sentence tagged: {pos_tagged_2}')
print('*' * 20)
#

# TODO: consider moving to the text_utils - packing
pos_tagged_1_prepared = []
for i, pos_tagged in enumerate(pos_tagged_1):
    pos_tagged_1_prepared.append((sentence.split()[i], pos_tagged))

pos_tagged_2_prepared = []
for i, pos_tagged in enumerate(pos_tagged_2):
    pos_tagged_2_prepared.append((sentence_2.split()[i], pos_tagged))


chunk_tree_1 = ntc.parse(pos_tagged_1_prepared)
print(f'1 chunk_tree: {chunk_tree_1}')
print(list(chunk_tree_1.subtrees()))
print('*' * 20)
chunk_tree_2 = ntc.parse(pos_tagged_2_prepared)
print(f'2 chunk_tree: {chunk_tree_2}')
print(list(chunk_tree_2.subtrees()))
