import json
import spacy


def parse_text_to_sentence(text, lang):

    with open('language Tables/combinedTable.json', 'r') as file:
        langTable = json.load(file)

    try:
        model = langTable[lang]['model']
        nlp = spacy.load('Segmentation Models/%s' % model)
    except:
        model = 'english'
        nlp = spacy.load('Segmentation Models/%s' % model)

    doc = nlp(text)
    return [sent.text for sent in list(doc.sents)]