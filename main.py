# This is a sample Python script.
import collections
import pickle
import threading
import time
from tempfile import TemporaryFile, NamedTemporaryFile
from tkinter import END, CENTER
import deepl

import pandas
from deep_translator import GoogleTranslator
import re
from playsound3 import playsound
from gtts import gTTS
import tkinter as tk
import os

# Load Config
deeplAuthKey = "4686f7b7-48e1-4c1d-8f63-07e55f927c40:fx"

QUEUE_MAXLEN = 5


class atlasInfo:
    def __init__(self):
        self.newCards = None
        self.index = None
        self.sentences = None
        self.transObj = None
        self.translation = None
        self.original = None
        self.sepTrans = None
        self.transQueue = collections.deque(maxlen=QUEUE_MAXLEN)
        self.currentTrans = None
        self.translationLabel = None
        self.originalLabel = None
        self.sepTransLabel = None
        self.window = None
        self.state = None


class sentenceTranslation:
    def __init__(self, index, original):
        # self.UID = UID
        self.index = index
        self.ready = False
        self.original = original
        self.translation = None
        self.separatedTranslation = None
        self.voice = None
        # self.sepTrans = translator([original])


class translatorObj:
    def __init__(self, transType, translator, source_lang, target_lang):
        self.targetLang = target_lang
        self.sourceLang = source_lang
        self.translator = translator
        self.transType = transType


def deeplTranslate(translator, original):
    return translator.translate_text(text=original, target_lang="EN-US")


def googleTranslate(translator, original):
    return translator.translate(text=original)


def translate(transObj, text):
    if transObj.transType == 'google':
        try:
            return transObj.translator.translate(text=text)
        except:
            return "Error in Translation"
    elif transObj.transType == 'deepl':
        try:
            results = transObj.translator.translate_text(text=text, target_lang=transObj.targetLang)
            if isinstance(results, list):
                return " | ".join([result.text for result in results])
            else:
                return results.text
        except:
            return "Error in Translation"
    else:
        raise Exception("Invalid Translator Type")


def translateVoice(transObj, text):
    voiceMp3 = NamedTemporaryFile()
    voice = gTTS(text=text, lang=transObj.sourceLang)
    voice.write_to_fp(voiceMp3)
    return voiceMp3


def playVoice(voice):
    playsound(voice.name, block=False)


def populateTranslation(atlas, sentenceTrans):
    sentenceTrans.translation = translate(atlas.transObj, sentenceTrans.original)
    sentenceTrans.separatedTranslation = translate(atlas.transObj, sentenceTrans.original.split())
    sentenceTrans.voice = translateVoice(atlas.transObj, sentenceTrans.original)
    sentenceTrans.ready = True


def addTranslationByIndex(atlas, index, mode):
    newTrans = sentenceTranslation(index, atlas.sentences[index])
    if mode == 'left':
        print("adding left")
        atlas1.transQueue.appendleft(newTrans)
    elif mode == 'right':
        print("adding right")
        atlas1.transQueue.append(newTrans)
    else:
        raise Exception("Invalid mode")
    x = threading.Thread(target=populateTranslation, args=(atlas, newTrans), daemon=True)
    x.start()


def fillQueue(atlas):
    if len(atlas.transQueue) == 0:
        addTranslationByIndex(atlas, atlas.index, 'right')
    while len(atlas.transQueue) < atlas.transQueue.maxlen:
        lastElement = atlas.transQueue.pop()
        lastIndex = lastElement.index
        atlas.transQueue.append(lastElement)
        addTranslationByIndex(atlas, lastIndex + 1, 'right')


atlas1 = atlasInfo()

# Initialize and shift files
if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards - Depreciated.txt"):
    os.remove("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards - Depreciated.txt")
if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards.txt"):
    old_file = os.path.join("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/", "Buy New Cards.txt")
    new_file = os.path.join("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/", "Buy New Cards - Depreciated.txt")
    os.rename(old_file, new_file)

# Read document with sentences
data = pandas.read_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Dan Brown - Kod Leonarda da Vinci (2004).tsv",
                       header=0, index_col=0,
                       sep='\t')
# Isolate sentences and initalize state
print(data)
sentences = data["Sentence"]
print(sentences)
atlas1.sentences = sentences
atlas1.index = None
atlas1.newCards = 0
atlas1.state = "original"
# original = translation = sepTrans = None

# Initialize index variable from file
with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'rb') as file:
    atlas1.index = pickle.load(file) - 2
print("Index: " + str(atlas1.index) + " " + str('%.2f' % ((atlas1.index / len(sentences)) * 100)) + "%")

# Initialize google translator
atlas1.googleTranslator = GoogleTranslator(source='polish', target='english')
# Initialize deepl translator
atlas1.deeplTranslator = deepl.DeepLClient(deeplAuthKey)

atlas1.transObj = translatorObj("deepl", atlas1.deeplTranslator, "pl", "EN-US")

atlas1.window = tk.Tk()
textFrame = tk.Frame(master=atlas1.window, width=200, height=100, bg="red")
textFrame.pack(fill=tk.BOTH, expand=True)
# translationLabel = tk.Label(master=textFrame, text='it me', font=("Arial", 25))
atlas1.translationLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
# translationLabel.configure(text = "it me")
atlas1.translationLabel.configure(text="it me")
atlas1.translationLabel.pack(fill=tk.X)
# originalLabel = tk.Label(master=textFrame, font=("Arial", 25))
atlas1.originalLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
atlas1.originalLabel.pack(fill=tk.X)
# sepTransLabel = tk.Label(master=textFrame, font=("Arial", 25))
atlas1.sepTransLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
atlas1.sepTransLabel.pack(fill=tk.X)
textFrame.pack()
atlas1.window.geometry("1000x450")
atlas1.window.title("HERKUSNEEZE")


# atlas1 = atlasInfo(index, translator, translation, original, sepTrans, translationLabel, originalLabel, sepTransLabel, window, newCards)
def showNewTemplate(atlas):
    # global index, translator, translation, original, sepTrans, translationLabel, originalLabel, sepTransLabel, window

    for i in range(2):
        try:
            fillQueue(atlas1)
            newTrans = atlas.transQueue.popleft()
            if newTrans.index != atlas.index:
                raise Exception("Invalid Index")
            else:
                atlas.currentTrans = newTrans
                break
        except Exception as e:
            print(e)
            atlas.transQueue.clear()

    while not atlas1.currentTrans.ready:
        print("snoozin")
        time.sleep(1)

    atlas.translationLabel.configure(text="")
    atlas.originalLabel.configure(text="Translating...")
    atlas.sepTransLabel.configure(text="")
    atlas.window.update_idletasks()

    #atlas.original = atlas1.sentences[atlas.index]

    # while len(original) > 60:
    #     print("Skipped Sentence")
    #     index += 1
    #     original = sentences[index]
    #atlas.translation = atlas.googleTranslator.translate(text=atlas.original)
    #print(atlas.translation)
    #print(deeplTranslate(atlas.deeplTranslator, atlas.original))

    print("Showing: %s" % (atlas.index))
    atlas.translationLabel.configure(text=atlas.currentTrans.translation)
    atlas.window.update_idletasks()

    # if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3"):
    #     os.remove("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
    # voice = gTTS(text=atlas.original, lang='pl', slow=False)
    # voice.save("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")

    # nopunc = re.sub(r'[^\w\s]', '', atlas.original)
    # nopunc = nopunc.split()
    # nopunc = [word for word in nopunc if not word.isnumeric()]
    # try:
    #     transwords = atlas.googleTranslator.translate_batch(nopunc)
    # except:
    #     transwords = ['Error in Translation']
    # atlas.sepTrans = " ".join(transwords)

    atlas.originalLabel.configure(text="")


def showOriginal(atlas):
    # global index, original, originalLabel, window, sepTrans
    atlas.originalLabel.configure(text=atlas.currentTrans.original)
    atlas.sepTransLabel.configure(text=atlas.currentTrans.separatedTranslation)
    atlas.window.update_idletasks()
    playVoice(atlas.currentTrans.voice)
    #playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3", False)
    # atlas.index += 1
    # with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'wb') as file:
    #     pickle.dump(atlas.index, file)


def appendToAnki(atlas):
    # global original, translation, newCards

    with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards.txt", 'a', encoding='utf-8') as deck:
        # Add quotations around sentences to avoid anki reading semicolons
        newCard = "\"%s\";\"%s\"\n" % (atlas.currentTrans.translation, atlas.currentTrans.original)
        atlas.newCards += 1
        deck.write(newCard)
    print("Added to deck, %d new cards" % atlas.newCards)


def advanceState(atlas):
    if atlas.state == "translation":
        atlas.state = "original"
        showOriginal(atlas)
    else:
        atlas.state = "translation"
        atlas.index += 1
        with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'wb') as indexfile:
            pickle.dump(atlas.index, indexfile)
        showNewTemplate(atlas)


def revertOne(atlas):
    # global index, state

    atlas.index -= 1
    # if atlas.state == "original":
    #     atlas.index -= 1
    atlas.transQueue.appendleft(atlas.currentTrans)
    addTranslationByIndex(atlas, atlas.index, 'left')
    atlas.state = "translation"
    showNewTemplate(atlas)


def playAudio(atlas):
    # playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
    playVoice(atlas.currentTrans.voice)


def handle_keypress(event):
    if event.char == ' ':
        advanceState(atlas1)
        return
    elif event.char == 'q':
        # Replay audio
        playAudio(atlas1)
        return
    elif event.char == '1':
        revertOne(atlas1)
        return
    elif event.char == '2':
        return
    elif event.char == '3':
        return
    elif event.char == '4':
        # Add to anki file
        appendToAnki(atlas1)
        return


atlas1.window.bind("<Key>", handle_keypress)
atlas1.window.mainloop()
