from spellchecker import SpellChecker
from textblob import Word
import csv
import numpy as np
import re
from nltk.corpus import words

def clean(tweet):
    raw_word_list = tweet.split(' ')
    word_list = []
    for w in raw_word_list:
        if not w.startswith("@") and not w.startswith("&") and not w.startswith("#"):
            w = w.strip(".!,\"")
            if w:
                word_list.append(w.strip(".!,"))
    return word_list


def valid(tweet):
    word_list = clean(tweet)
    if len(word_list) < 10:
        return False
    if SpellChecker().unknown(word_list):
        return False
    for w in word_list:
        if w != Word(w).spellcheck()[0][0]:
            return False
    return word_list


output = []
with open('data/hatespeech.csv', 'r') as f:
    data = list(csv.reader(f, delimiter=","))

data = np.array(data)
for i in range(1, len(data)):
    if len(output) >= 1000:
        break
    print(i, len(output))
    sentences = re.split(': |_|-|!|;|,|\.', data[i][6])
    for sentence in sentences:
        wl = valid(sentence)
        if wl:
            output.append(" ".join(wl))

text_file = open("data/clean_sentences.txt", "w")
for e in output:
    text_file.write(e + "\n")
text_file.close()
