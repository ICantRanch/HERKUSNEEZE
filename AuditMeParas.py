import os

import pandas as pd
import nltk


def parseTxt(filePath, newFilePath):
    with open(filePath, "r", encoding='utf-8') as file:
        lines = nltk.sent_tokenize(file.read())
    lines = list(filter(None, lines))

    df = pd.DataFrame(lines, columns=['Sentence'])
    df.to_csv(newFilePath, sep='\t')
