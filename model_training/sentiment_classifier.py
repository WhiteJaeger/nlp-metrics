import random
import re
import string

from joblib import dump
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.corpus import twitter_samples, stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize


def remove_noise(tokens_collection: list, stop_words: tuple = ()):
    cleaned_tokens = []

    for token, tag in pos_tag(tokens_collection):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
        token = re.sub("(@[A-Za-z0-9_]+)", "", token)

        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        forbidden = ':) :-) :( :-( :d rt … ...'.split()

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words and \
                token.lower() not in forbidden:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


def get_all_words(cleaned_tokens: list):
    for tokens_collection in cleaned_tokens:
        for token in tokens_collection:
            yield token


def get_tweets_for_model(cleaned_tokens: list):
    for tokens_collection in cleaned_tokens:
        yield dict([token, True] for token in tokens_collection)


if __name__ == "__main__":

    stop_words_eng = stopwords.words('english')

    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')
    neutral_tweet_tokens = twitter_samples.tokenized('tweets.20150430-223406.json')

    positive_cleaned_tokens = []
    negative_cleaned_tokens = []
    neutral_cleaned_tokens = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens.append(remove_noise(tokens, stop_words_eng))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens.append(remove_noise(tokens, stop_words_eng))

    for tokens in neutral_tweet_tokens:
        neutral_cleaned_tokens.append(remove_noise(tokens, stop_words_eng))

    neutral_cleaned_tokens = neutral_cleaned_tokens[:5000]

    all_cleaned_tokens = positive_cleaned_tokens + negative_cleaned_tokens + neutral_cleaned_tokens

    all_pos_words = get_all_words(all_cleaned_tokens)

    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(10))

    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens)
    neutral_tokens_for_model = get_tweets_for_model(neutral_cleaned_tokens)

    positive_dataset = [(tweet_dict, "Positive")
                        for tweet_dict in positive_tokens_for_model]

    negative_dataset = [(tweet_dict, "Negative")
                        for tweet_dict in negative_tokens_for_model]

    neutral_dataset = [(tweet_dict, "Neutral")
                       for tweet_dict in neutral_tokens_for_model]

    dataset = positive_dataset + negative_dataset + neutral_dataset
    print(f'DATASET SIZE: {len(dataset)}')

    random.shuffle(dataset)

    train_data = dataset[:10000]
    test_data = dataset[10000:]

    classifier = NaiveBayesClassifier.train(train_data)

    print('Accuracy is: ', classify.accuracy(classifier, test_data))

    print(classifier.show_most_informative_features(10))

    custom_tweet = 'I ordered just once from Bad Company, they screwed up, never used the app again.'

    custom_tokens = remove_noise(word_tokenize(custom_tweet))

    print(custom_tweet, classifier.classify(dict([token, True] for token in custom_tokens)))

    # Save model
    dump(classifier, 'sentiment_classifier.joblib')
