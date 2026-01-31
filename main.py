import json
import pickle
import time
from tkinter import CENTER
import deepl

import pandas
from deep_translator import GoogleTranslator
from googletrans import Translator as googletransTranslator
import tkinter as tk
from tkinter import ttk
import os
import configparser
import uuid

from Atlas import atlasInfo
from AuditMeParas import parseTxt


deeplAuthKey = "4686f7b7-48e1-4c1d-8f63-07e55f927c40:fx"

def addNewText():
    filepath = tk.filedialog.askopenfilename()
    if not os.path.exists(filepath):
        tk.messagebox.showwarning("New Text Selection", "Invalid File Path")
        return
    initialFilePath = 'Converted Texts/'
    os.makedirs(initialFilePath, exist_ok=True)
    fileName = os.path.splitext(os.path.basename(filepath))[0]
    parsedFilePath = "%s%s.tsv" % (initialFilePath, fileName)
    parseTxt(filepath, parsedFilePath)
    parsedData = pandas.read_csv(parsedFilePath,
                           header=0, index_col=0,
                           sep='\t')
    sampleSentence = parsedData["Sentence"][10]
    result = tk.messagebox.askquestion(title="Confirmation", message="Does the following sentence look correct?\n\n%s" % sampleSentence)
    if result != 'yes':
        print("non")

    detectedLang = detectTrans.detect(sampleSentence).lang

    with open("language Tables/googleTable.json", "r") as file:
        googles = json.load(file)

    textInfo = {fileName: {"ID": uuid.uuid1().hex, "index": 0, "lang": googles[detectedLang]}}

    with open("atlasTextData.json", "r+") as file:
        jsonData = json.load(file)
        jsonData.update(textInfo)
        file.seek(0)
        json.dump(jsonData, file, indent=4)

def newConfig():

    config = configparser.ConfigParser()
    config.read('default.ini')
    with open('atlasConfig.ini', 'w') as configfile:
        config.write(configfile)
    editConfig()

def editConfig():

    #Config:
    #Native Lang
    #Google or deepl
    #deepl api key
    #Current text

    def saveConfig():
        config['Atlas']['nativeLang'] = languageSelector.get().lower()

        if deeplApiEntry.get() != '':
            validation = validateTranslator(deeplApiEntry.get())
            if validation:
                config['Atlas']['deeplapikey'] = deeplApiEntry.get()
            else:
                tk.messagebox.showwarning("DeepL Validation", "The inputted DeepL api key is invalid")
                config['Atlas']['deeplapikey'] = ''
            config['Atlas']['deepl'] = str(validation)

        config['Atlas']['currentText'] = textSelector.get()

        with open('atlasConfig.ini', 'w') as configfile:
            config.write(configfile)
        popup.destroy()
        atlas1['atlas'] = initializeAtlas()

    def addTextHelper():
        addNewText()
        with open("atlasTextData.json", "r") as file:
            availableTexts = list(json.load(file).keys())
        textSelector['values'] = availableTexts

    popup = tk.Toplevel(window)
    popup.geometry('350x350')
    popup.transient(window)

    config = configparser.ConfigParser()
    config.read('atlasConfig.ini')

    with open("Language Tables/combinedTable.json", "r") as file:
        combinedTable = json.load(file)

    availableLanguages = [language.capitalize() for language in list(combinedTable.keys())]

    languageSelector = tk.ttk.Combobox(popup, values=availableLanguages)
    currentLang = config['Atlas']['nativeLang'].capitalize()
    if currentLang in availableLanguages:
        languageSelector.set(currentLang)
    languageSelector.pack(padx=5, pady=5)

    deeplApiEntry = tk.ttk.Entry(popup)
    deeplApiEntry.insert(0, config['Atlas']['deeplapikey'])
    deeplApiEntry.pack()

    addTextButton = tk.ttk.Button(popup, text="Add New Text", command=addTextHelper)
    addTextButton.pack()

    with open("atlasTextData.json", "r") as file:
        availableTexts = list(json.load(file).keys())

    textSelector = tk.ttk.Combobox(popup, values=availableTexts)
    if config['Atlas']['currentText'] in availableTexts:
        textSelector.set(config['Atlas']['currentText'])
    textSelector.pack(padx=5, pady=5)

    saveButton = tk.ttk.Button(popup, text="Save Config", command=saveConfig)
    saveButton.pack()

    window.wait_window(popup)

def validateTranslator(apikey):
    try:
        deepl.DeepLClient(apikey).get_usage()
        return True
    except:
        return False

def loadConfig():
    for i in range(2):
        try:
            # If config doesn't exist create new config
            open('atlasConfig.ini', 'r')
            config = configparser.ConfigParser()
            config.read('atlasConfig.ini')
            return config
        except:
            newConfig()
def handle_keypress(event):
    atlas2 = atlas1['atlas']
    if event.char == ' ':
        advanceState(atlas2)
        return
    elif event.char == 'q':
        # Replay audio
        playAudio(atlas2)
        return
    elif event.char == '1':
        revertOne(atlas2)
        return
    elif event.char == '2':
        return
    elif event.char == '3':
        return
    elif event.char == '4':
        # Add to anki file
        appendToAnki(atlas2)
        return
def initializeAtlas():

    try:
        # Load Config
        config = loadConfig()

        with open("Output/Saved Cards - Last Session.txt", 'w') as file:
            file.close()
        newAtlas = atlasInfo()

        #Load Text Data
        with open("atlasTextData.json", "r") as file:
            textData = json.load(file)
        currentText = (config['Atlas']['currentText'], textData[config['Atlas']['currentText']])

        newAtlas.text = currentText[0]
        newAtlas.index = currentText[1]['index']

        #Load Language Table
        with open("Language Tables/combinedTable.json", "r") as file:
            combinedTable = json.load(file)

        newAtlas.initializeTranslator(combinedTable[currentText[1]['lang']], combinedTable[config['Atlas']['nativelang']], config['Atlas'].getboolean('deepl'), config['Atlas']['deeplapikey'])

        filepath = 'Converted Texts/%s.tsv' % config['Atlas']['currentText']
        print(filepath)
        data = pandas.read_csv(filepath,
                       header=0, index_col=0,
                       sep='\t')
        newAtlas.sentences = list(data["Sentence"])

        window.bind("<Key>", handle_keypress)

        translationLabel.configure(text="Welcome to Atlas")
        originalLabel.configure(text="Advance to continue")

        return newAtlas
    except Exception as e:
        print(e)
        translationLabel.configure(text="No text selected")
        originalLabel.configure(text="Texts can be added and selected in the configuration menu")
        sepTransLabel.configure(text='')
        pass


# atlas1 = atlasInfo()

detectTrans = googletransTranslator(service_urls=['translate.google.com'])

window = tk.Tk()
textFrame = tk.Frame(master=window, width=200, height=100, bg="red")
textFrame.pack(fill=tk.BOTH, expand=True)
translationLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
# translationLabel.configure(text="Welcome to Atlas")
translationLabel.pack(fill=tk.X)
originalLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
# originalLabel.configure(text="Advance to continue")
originalLabel.pack(fill=tk.X)
sepTransLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
sepTransLabel.pack(fill=tk.X)
textFrame.pack()

Menu = tk.Menu(textFrame)
Menu.add_command(label='Add Text', command=addNewText)
Menu.add_command(label='Edit Config', command=editConfig)
window.config(menu=Menu)

atlas1 = {'atlas': initializeAtlas()}

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

    translationLabel.configure(text="")
    sepTransLabel.configure(text="")

    while not atlas.currentTrans.ready:
        print("snoozin")
        originalLabel.configure(text="Translating...")
        window.update_idletasks()
        time.sleep(1)

    originalLabel.configure(text="")
    window.update_idletasks()

    print("Showing: %s" % atlas.index)
    translationLabel.configure(text=atlas.currentTrans.translation)
    window.update_idletasks()


def showOriginal(atlas):
    originalLabel.configure(text=atlas.currentTrans.original)
    sepTransLabel.configure(text=atlas.currentTrans.separatedTranslation)
    window.update_idletasks()
    atlas.currentTrans.playVoice()


def appendToAnki(atlas):
    with open("Output/Saved Cards - Last Session.txt", 'a', encoding='utf-8') as lastsession, open("Output/Saved Cards - Total.txt", 'a', encoding='utf-8') as total:
        newCard = "\"%s\";\"%s\"\n" % (atlas.currentTrans.translation, atlas.currentTrans.original)
        atlas.newCards += 1
        lastsession.write(newCard)
        total.write(newCard)
    print("Added to deck, %d new cards" % atlas.newCards)


def updateIndex(atlas):
    with open("atlasTextData.json", "r+") as file:
        textData = json.load(file)
        textData[atlas.text]['index'] = atlas.index
        file.seek(0)
        json.dump(textData, file, indent=4)

def advanceState(atlas):
    if atlas.state == "translation":
        atlas.state = "original"
        showOriginal(atlas)
    else:
        atlas.state = "translation"
        atlas.index += 1
        updateIndex(atlas)
        showNewTemplate(atlas)


def revertOne(atlas):
    atlas.index -= 1
    atlas.transQueue.appendleft(atlas.currentTrans)
    atlas.addTranslationByIndex(atlas.index, 'left')
    atlas.state = "translation"
    showNewTemplate(atlas)


def playAudio(atlas):
    atlas.currentTrans.playVoice()


window.mainloop()


