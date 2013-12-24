"""Constants and functions for lexicon-based sentiment analysis.

Public module constants:
    positive_words: A frozen set of positive sentiment words.
    negative_words: A frozen set of negative sentiment words.
"""


import string

with open('/path/to/lexicons/opinion_lexicon/positive_words.txt') as f:
    positive_words = frozenset(i.rstrip() for i in f.readlines()
                               if not (i.startswith(';') or len(i) == 0))

with open('/path/to/lexicons/opinion_lexicon/negative_words.txt') as f:
    negative_words = frozenset(i.rstrip() for i in f.readlines()
                               if not (i.startswith(';') or len(i) == 0))

def preprocess(text):
    """Preprocess text into a bag of words.

    Args:
        text: A string of text.

    Returns:
        A list of token strings.
    """
    text = text.lower().split()
    text = [i for i in text if not i.startswith(('#', 'http', '@'))]
    text = [i.strip(string.punctuation) for i in text]
    return text


def score(bag_of_words, positive_words, negative_words):
    """Perform lexicon-based sentiment analysis.

    Args:
        bag_of_words: A list of tokens in a sentence.
        positive_words: A set of positive sentiment words.
        negative_words: A set of negative sentiment words.

    Returns:
        A (positive sentiment, negative sentiment) tuple of unsigned
            integers corresponding to the sentiment word frequencies.
    """
    p, n = 0, 0
    for word in bag_of_words:
        if word in positive_words:
            p += 1
        elif word in negative_words:
            n += 1
        else:
            continue
    return (p, n)


