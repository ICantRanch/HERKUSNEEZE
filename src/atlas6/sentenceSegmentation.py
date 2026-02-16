import json
import spacy
import spacy_pkuseg


def text_to_chunks(text):
    chunk_size = 48000
    textbytes = text.encode('utf-8')
    chunksbytes = [textbytes[i:i + chunk_size] for i in range(0, len(textbytes), chunk_size)]
    i = 0
    prev = 0
    textchunks = []
    while i < len(textbytes):
        i += chunk_size
        for ii in range(3):
            try:
                bytechunk = textbytes[prev:i + ii]
                textchunk = bytechunk.decode('utf-8')
                textchunks.append(textchunk)
                prev = i + ii
                break
            except UnicodeDecodeError:
                pass
    return textchunks

def parse_text_to_sentence(text, lang, result):

    with open('language Tables/combinedTable.json', 'r') as file:
        langTable = json.load(file)

    try:
        model = langTable[lang]['model']
        nlp = spacy.load('Segmentation Models/%s' % model)
    except Exception as e:
        print(e)
        model = 'english'
        nlp = spacy.load('Segmentation Models/%s' % model)

    if model == 'japanese':
        # Split text
        docs = list(nlp.pipe(text_to_chunks(text)))
        resulttemp = []
        [resulttemp.extend([sent.text for sent in list(doc.sents)]) for doc in docs]
        result[0] = resulttemp
    else:
        doc = nlp(text)
        result[0] = [sent.text for sent in list(doc.sents)]