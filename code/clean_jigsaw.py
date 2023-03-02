from spellchecker import SpellChecker
from textblob import Word
import csv
import numpy as np
import re
from tqdm import tqdm


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
with open('data/jigsaw.csv', 'r') as f:
    data = list(csv.reader(f, delimiter=","))

print(len(data))
print(data[0])
print(data[1])
print(data[2])
print('done')
for i in tqdm(range(1, len(data))):
    if float(data[i][13]) > 0.7:
        sentences = re.split(': |_|-|!|;|,|\.', data[i][1])
        for sentence in sentences:
            wl = valid(sentence)
            if wl:
                output.append(" ".join(wl))


text_file = open("data/clean_sentences_jig.txt", "w")
for e in output:
    text_file.write(e + "\n")
text_file.close()
