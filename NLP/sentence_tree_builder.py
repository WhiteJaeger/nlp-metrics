from abc import ABC

import sklearn
from nltk.chunk import ChunkParserI
from nltk.chunk.util import conlltags2tree, tree2conlltags
from nltk.corpus import conll2000
from nltk.tag import BigramTagger, UnigramTagger

data = list(conll2000.chunked_sents())
train_data, test_data = sklearn.model_selection.train_test_split(data, test_size=0.2, random_state=1234)


# define the chunker class
class NGramTagChunker(ChunkParserI, ABC):

    def __init__(self, train_sentences,
                 tagger_classes=(UnigramTagger, BigramTagger)):
        train_sent_tags = self.conll_tag_chunks(train_sentences)
        self.chunk_tagger = self.combined_tagger(train_sent_tags, tagger_classes)

    def parse(self, tagged_sentence):
        if not tagged_sentence:
            return None
        pos_tags = [tag for word, tag in tagged_sentence]
        chunk_pos_tags = self.chunk_tagger.tag(pos_tags)
        chunk_tags = [chunk_tag for (pos_tag, chunk_tag) in chunk_pos_tags]
        wpc_tags = [(word, pos_tag, chunk_tag) for ((word, pos_tag), chunk_tag)
                    in zip(tagged_sentence, chunk_tags)]
        return conlltags2tree(wpc_tags)

    @staticmethod
    def conll_tag_chunks(chunk_sents):
        tagged_sents = [tree2conlltags(tree) for tree in chunk_sents]
        return [[(t, c) for (w, t, c) in sent] for sent in tagged_sents]

    @staticmethod
    def combined_tagger(train_, taggers, backoff=None):
        for tagger in taggers:
            backoff = tagger(train_, backoff=backoff)
        return backoff


#
# train chunker model
SENTENCE_TREE_BUILDER = NGramTagChunker(train_data)
#
# evaluate chunker model performance
# print(ntc.evaluate(test_data))