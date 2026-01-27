import json
import pickle
import time
from tkinter import CENTER
import deepl

import pandas
from deep_translator import GoogleTranslator
from googletrans import Translator as googletransTranslator
import tkinter as tk
import os
import configparser
import uuid

from Atlas import atlasInfo
from AuditMeParas import parseTxt

# Load Config
config = configparser.ConfigParser()
config['DEFAULT'] = {'test':'youbetcha'}
with open('example.ini', 'w') as configfile:
    config.write(configfile)

deeplAuthKey = "4686f7b7-48e1-4c1d-8f63-07e55f927c40:fx"

def addNewText():
    filepath = tk.filedialog.askopenfilename()
    initialFilePath = 'Converted Texts/'
    os.makedirs(initialFilePath, exist_ok=True)
    fileName = os.path.splitext(os.path.basename(filepath))[0]
    parsedFilePath = "%s%s.tsv" % (initialFilePath, fileName)
    parseTxt(filepath, parsedFilePath)
    parsedData = pandas.read_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Dan Brown - Kod Leonarda da Vinci (2004).tsv",
                           header=0, index_col=0,
                           sep='\t')
    sampleSentence = parsedData["Sentence"][10]
    result = tk.messagebox.askquestion(title="Confirmation", message="Does the following sentence look correct?\n\n%s" % sampleSentence)
    if result != 'yes':
        print("non")

    detectedLang = detectTrans.detect(sampleSentence).lang

    with open("googleTable.json", "r") as file:
        googles = json.load(file)

    textInfo = {fileName: {"ID": uuid.uuid1().hex, "index": 0, "lang": googles[detectedLang]}}

    with open("atlasTextData.json", "r+") as file:
        jsonData = json.load(file)
        jsonData.update(textInfo)
        file.seek(0)
        json.dump(jsonData, file, indent=4)
def editConfig():

    #Config:
    #Native Lang
    #Google or deepl
    #deepl api key
    #Current text

    popup = tk.Toplevel(window)


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

# Initialize index variable from file
with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'rb') as file:
    atlas1.index = pickle.load(file) - 1

# with open("atlasTextData.json", "r+") as file:
#     jsonData = json.load(file)
#     atlas1.index = jsonData[textName]["index"]

print("Index: " + str(atlas1.index) + " " + str('%.2f' % ((atlas1.index / len(sentences)) * 100)) + "%")

detectTrans = googletransTranslator(service_urls=['translate.google.com'])
# Initialize google translator
atlas1.googleTranslator = GoogleTranslator(source='auto', target='english')
# Initialize deepl translator
atlas1.deeplTranslator = deepl.DeepLClient(deeplAuthKey)


atlas1.transObj = atlasInfo.translatorObj("deepl", atlas1.deeplTranslator, "pl", "EN-US")

window = tk.Tk()
textFrame = tk.Frame(master=window, width=200, height=100, bg="red")
textFrame.pack(fill=tk.BOTH, expand=True)
# translationLabel = tk.Label(master=textFrame, text='it me', font=("Arial", 25))
atlas1.translationLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
# translationLabel.configure(text = "it me")
atlas1.translationLabel.configure(text="Welcome to Atlas")
atlas1.translationLabel.pack(fill=tk.X)
# originalLabel = tk.Label(master=textFrame, font=("Arial", 25))
atlas1.originalLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
atlas1.originalLabel.configure(text="Advance to continue")
atlas1.originalLabel.pack(fill=tk.X)
# sepTransLabel = tk.Label(master=textFrame, font=("Arial", 25))
atlas1.sepTransLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
atlas1.sepTransLabel.pack(fill=tk.X)
textFrame.pack()

Menu = tk.Menu(textFrame)
Menu.add_command(label='Add Text', command=addNewText)
window.config(menu=Menu)

window.geometry("1000x450")
window.title("HERKUSNEEZE")


def showNewTemplate(atlas):
    for i in range(2):
        try:
            atlas.fillQueue()
            newTrans = atlas.transQueue.popleft()
            if newTrans.index != atlas.index:
                raise Exception("Invalid Index")
            else:
                atlas.currentTrans = newTrans
                break
        except Exception as e:
            print(e)
            atlas.transQueue.clear()

    atlas.translationLabel.configure(text="")
    atlas.sepTransLabel.configure(text="")

    while not atlas.currentTrans.ready:
        print("snoozin")
        atlas.originalLabel.configure(text="Translating...")
        window.update_idletasks()
        time.sleep(1)

    atlas.originalLabel.configure(text="")
    window.update_idletasks()

    print("Showing: %s" % atlas.index)
    atlas.translationLabel.configure(text=atlas.currentTrans.translation)
    window.update_idletasks()


def showOriginal(atlas):
    atlas.originalLabel.configure(text=atlas.currentTrans.original)
    atlas.sepTransLabel.configure(text=atlas.currentTrans.separatedTranslation)
    window.update_idletasks()
    atlas.currentTrans.playVoice()


def appendToAnki(atlas):
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
    atlas.index -= 1
    atlas.transQueue.appendleft(atlas.currentTrans)
    atlas.addTranslationByIndex(atlas.index, 'left')
    atlas.state = "translation"
    showNewTemplate(atlas)


def playAudio(atlas):
    atlas.currentTrans.playVoice()


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


window.bind("<Key>", handle_keypress)
window.mainloop()
