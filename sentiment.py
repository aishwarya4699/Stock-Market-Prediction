from textblob import TextBlob
from enum import Enum


class Sentiments(Enum):
    positive = 1
    negative = -1
    neutral = 0


def classify(text):
    pol = TextBlob(text).polarity

    if pol > 0:
        return 1

    elif pol < 0:
        return -1

    else:
        return 0
