import re
import nltk
from constants import CONTRACTION_MAP
from nltk.tokenize.toktok import ToktokTokenizer
from NLP.pos import features

stopword_list = nltk.corpus.stopwords.words('english')
stopword_list.remove('no')
stopword_list.remove('not')


def prepare_str(text: str, contraction_expansion=True, text_lower_case=False,
                special_char_removal=True,
                stopword_removal=False, remove_digits=False, pos_preparation=False):

    # expand contractions
    if contraction_expansion:
        text = expand_contractions(text)

    # lowercase the text
    if text_lower_case:
        text = text.lower()

    # remove special characters and\or digits
    if special_char_removal:
        # insert spaces between special characters to isolate them
        special_char_pattern = re.compile(r'([{.(-)!}])')
        text = special_char_pattern.sub(" \\1 ", text)
        text = remove_special_characters(text, remove_digits=remove_digits)
        # remove extra whitespace
        text = re.sub(' +', ' ', text)

    # remove stopwords
    if stopword_removal:
        text = remove_stopwords(text, is_lower_case=text_lower_case)

    if pos_preparation:
        # TODO: consider splitting text into sentences
        text = [text.split()]

        prepared_text = []
        for sentences in text:
            prepared_text.append([features(sentences, index) for index in range(len(sentences))])
        return prepared_text

    return text


def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    """
    Utils function to transform contractions into the normalized format.

    Example usage:
        input_text = 'Y'all can't expand contractions I'd think'
        print(expand_contractions(input_text))

        Output: `You all cannot expand contractions I would think`
    """
    contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())),
                                      flags=re.IGNORECASE | re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match) \
            if contraction_mapping.get(match) \
            else contraction_mapping.get(match.lower())
        expanded_contraction = first_char + expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text


def remove_special_characters(text, remove_digits=False):
    """
    Utils function to remove special characters.
    """
    pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
    text = re.sub(pattern, '', text)
    return text


def remove_stopwords(text, is_lower_case=False):
    tokenizer = ToktokTokenizer()
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text


def map_word_pos(prepared_sentence: str, pos_tags: list) -> list:

    words = prepared_sentence.split()

    mapped = zip(words, pos_tags)

    return list(mapped)
