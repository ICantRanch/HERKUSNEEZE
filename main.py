import json
import time
from tkinter import CENTER
import deepl

import pandas
from langdetect import detect
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

    with open("language Tables/googleTable.json", "r") as file:
        googles = json.load(file)

    sampleSentence = parsedData["Sentence"][10]
    detectedLang = detect(sampleSentence)
    result = tk.messagebox.askquestion(title="Confirmation",
                                       message="Does the following sentence look correct?\n\n%s\n\nDetect Language: %s" % (
                                       sampleSentence, googles[detectedLang].capitalize()))
    if result != 'yes':
        print("non")
        return

    textInfo = {fileName: {"ID": uuid.uuid1().hex, "index": 0, "lang": googles[detectedLang]}}

    with open("atlasTextData.json", "a+") as file:
        file.seek(0)
        try:
            jsonData = json.load(file)
        except Exception as e:
            print(e)
            jsonData = {}
        jsonData.update(textInfo)
        file.truncate(0)
        json.dump(jsonData, file, indent=4)


def newConfig():
    config = configparser.ConfigParser()
    config.read('default.ini')
    with open('atlasConfig.ini', 'w') as configfile:
        config.write(configfile)
    editConfig()


def editConfig():
    def saveConfig():

        if languageSelector.get() in availableLanguages:
            config['Atlas']['nativeLang'] = languageSelector.get().lower()

        if deeplApiEntry.get() != '':
            validation = validateTranslator(deeplApiEntry.get())
            if validation and deeplApiEntry.get() != config['Atlas']['deeplapikey']:
                tk.messagebox.showinfo("DeepL Validation",
                                       "The inputted DeepL api key is valid, DeepL translation has been enabled")
                config['Atlas']['deeplapikey'] = deeplApiEntry.get()
            elif not validation:
                tk.messagebox.showwarning("DeepL Validation", "The inputted DeepL api key is invalid")
                config['Atlas']['deeplapikey'] = ''

            config['Atlas']['deepl'] = str(validation)

        if textSelector.get() in availableTexts:
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
    popup.title('Atlas Config')
    popup.geometry('500x550+%s+%s' % (round(window.winfo_x() + (window.winfo_width() / 4)), window.winfo_y() + 10))
    popup.transient(window)

    config = configparser.ConfigParser()
    config.read('atlasConfig.ini')

    with open("Language Tables/combinedTable.json", "r") as file:
        combinedTable = json.load(file)

    availableLanguages = [language.capitalize() for language in list(combinedTable.keys())]

    tk.Grid.columnconfigure(popup, 0, weight=1)
    # tk.Grid.rowconfigure(popup, 1, weight=1)

    languageFrame = tk.ttk.Labelframe(popup, text='Please Select Your Native Language')
    tk.Grid.rowconfigure(languageFrame, 0, weight=1)
    tk.Grid.columnconfigure(languageFrame, 0, weight=1)
    languageSelector = tk.ttk.Combobox(languageFrame, values=availableLanguages)

    currentLang = config['Atlas']['nativeLang'].capitalize()
    if currentLang in availableLanguages:
        languageSelector.set(currentLang)

    languageSelector.grid(row=0, column=0, sticky='EW', ipadx=10, ipady=10, padx=10, pady=10)
    languageFrame.grid(row=0, column=0, sticky='EW', padx=10, pady=10)

    deeplFrame = tk.ttk.Labelframe(popup, text='DeepL Configuration (Optional)')
    deeplFrame.grid(row=1, column=0, sticky='EW', padx=10, pady=10)
    tk.Grid.columnconfigure(deeplFrame, 0, weight=1)
    tk.Grid.rowconfigure(deeplFrame, 0, weight=1)

    deepllabel = tk.Message(master=deeplFrame, anchor=CENTER, justify=CENTER, width=300,
                            text='DeepL can offer better translations but an API key is required. A free API is available but requires a DeepL account and credit card information.\n If no valid api key is available, Google Translate will be used instead.')
    deepllabel.grid(row=0, column=0, sticky='EW', padx=10, pady=10)
    deeplApiEntry = tk.ttk.Entry(deeplFrame)
    deeplApiEntry.insert(0, config['Atlas']['deeplapikey'])
    deeplApiEntry.grid(row=1, column=0, sticky='NSEW', padx=10, pady=10)

    textSelectionFrame = tk.ttk.Labelframe(popup, text='Text Selection')
    textSelectionFrame.grid(row=2, column=0, sticky='EW', padx=10, pady=10)
    tk.Grid.columnconfigure(textSelectionFrame, 0, weight=1)
    tk.Grid.rowconfigure(textSelectionFrame, 0, weight=1)

    addTextLabel = tk.Message(textSelectionFrame, anchor=CENTER, justify=CENTER, width=300,
                              text='A Standard .txt file can be converted for use with this app. Any number of texts can be stored and switched between. The index for each text is unique, you can switch freely between texts without losing your spot.')
    addTextLabel.grid(row=0, column=0, sticky='EW', padx=10, pady=10)
    addTextButton = tk.ttk.Button(textSelectionFrame, text="Add New Text", command=addTextHelper)
    addTextButton.grid(row=2, column=0, sticky='EW', padx=10, pady=10)

    with open("atlasTextData.json", "r") as file:
        availableTexts = list(json.load(file).keys())

    textSelector = tk.ttk.Combobox(textSelectionFrame, values=availableTexts)
    if len(availableTexts) == 0:
        textSelector.set("No Texts Available. Add new texts to select.")
    elif config['Atlas']['currentText'] in availableTexts:
        textSelector.set(config['Atlas']['currentText'])
    else:
        textSelector.set('Please select a text.')
    textSelector.grid(row=1, column=0, sticky='EW', padx=10, pady=10)

    saveButton = tk.ttk.Button(popup, text="Save Config", command=saveConfig)
    saveButton.grid(row=3, column=0, sticky='NSEW', padx=10, pady=10)

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


def gotoIndex(atlas):
    newIndex = tk.simpledialog.askinteger('Go to index', 'What index would you like to go to?')
    try:
        if 0 <= newIndex <= len(atlas.sentences):
            atlas.index = newIndex
        else:
            raise Exception
    except:
        tk.messagebox.showwarning('Go to index', 'Invalid index')
        return
    updateIndex(atlas)
    atlas.state = "translation"
    showNewTemplate(atlas)


def setFontSize(newsize):
    mainfont.config(size=newsize)
    config = configparser.ConfigParser()
    config.read('atlasConfig.ini')
    config['Atlas']['textsize'] = newsize
    with open('atlasConfig.ini', 'w') as configfile:
        config.write(configfile)


def resizeLabels(event):
    if event.widget == window:
        labels = [translationLabel, originalLabel, sepTransLabel]
        for label in labels:
            label.configure(wraplength=round(event.width * 0.9))


def handle_keypress(input):
    atlas2 = atlas1['atlas']

    if isinstance(input, str):
        character = input
    else:
        try:
            character = input.char
        except:
            pass
    if character == ' ':
        advanceState(atlas2)
    elif character == 'q':
        # Replay audio
        playAudio(atlas2)
    elif character == '1':
        revertOne(atlas2)
    elif character == '4':
        # Add to anki file
        appendToAnki(atlas2)
    elif character == '5':
        # Go to a user inputed index
        gotoIndex(atlas2)


def initializeAtlas():
    try:
        # Load Config
        config = loadConfig()

        with open("Output/Saved Cards - Last Session.txt", 'w') as file:
            file.close()
        newAtlas = atlasInfo()

        # Load Text Data
        with open("atlasTextData.json", "r") as file:
            textData = json.load(file)
        currentText = (config['Atlas']['currentText'], textData[config['Atlas']['currentText']])

        newAtlas.text = currentText[0]
        newAtlas.index = max(currentText[1]['index'] - 1, -1)

        # Load Language Table
        with open("Language Tables/combinedTable.json", "r") as file:
            combinedTable = json.load(file)

        newAtlas.initializeTranslator(combinedTable[currentText[1]['lang']],
                                      combinedTable[config['Atlas']['nativelang']], config['Atlas'].getboolean('deepl'),
                                      config['Atlas']['deeplapikey'])

        filepath = 'Converted Texts/%s.tsv' % config['Atlas']['currentText']
        print(filepath)
        data = pandas.read_csv(filepath,
                               header=0, index_col=0,
                               sep='\t')
        newAtlas.sentences = list(data["Sentence"])

        window.bind("<Key>", handle_keypress)

        fontsizevar.set(config['Atlas']['textsize'])
        setFontSize(config['Atlas']['textsize'])

        translationLabel.configure(text="Welcome to Atlas")
        originalLabel.configure(text="Advance to continue")
        sepTransLabel.configure(text='')
        textNameLabel.configure(text=newAtlas.text)
        indexpercent = (newAtlas.index / len(newAtlas.sentences) * 100)
        textIndexLabel.configure(text='Index: %s | %.2f%%' % (newAtlas.index, indexpercent))

        return newAtlas
    except Exception as e:
        print(e)
        translationLabel.configure(text="Welcome to Atlas")
        originalLabel.configure(text="No text selected")
        sepTransLabel.configure(text='Texts can be added and selected in the configuration menu')
        pass


# atlas1 = atlasInfo()

window = tk.Tk()
window.geometry("1000x850")

mainfont = tk.font.Font(family='Arial', size=25)

tk.Grid.columnconfigure(window, 0, weight=1)
tk.Grid.rowconfigure(window, 0, weight=1)

textFrame = tk.Frame(master=window)
tk.Grid.columnconfigure(textFrame, 0, weight=1)
# tk.Grid.rowconfigure(textFrame, 0, weight=1)
textFrame.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
textFrame.rowconfigure((1, 2, 3), weight=1, uniform=1)

textInfoFrame = tk.ttk.Labelframe(textFrame, text='Text Info')
textInfoFrame.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)

textSizeFrame = tk.Frame(textInfoFrame)
textSizeFrame.columnconfigure(0, weight=1)
textSizeLabel = tk.Message(master=textSizeFrame, anchor=CENTER, justify=CENTER, font=mainfont, text='Text \nSize:')
textSizeLabel.grid(row=0, column=0, sticky='E')
fontsizevar = tk.IntVar(value=15)
textSizeChanger = tk.ttk.Spinbox(textSizeFrame, from_=1, to=50, textvariable=fontsizevar,
                                 command=lambda: setFontSize(textSizeChanger.get()))
textSizeFrame.grid(row=0, column=0, padx=10, pady=10)
textSizeChanger.grid(row=0, column=1, sticky='W')
textSizeFrame.columnconfigure((0,1), weight=1)


textNameLabel = tk.Message(master=textInfoFrame, anchor=CENTER, justify=CENTER, font=mainfont, width=950)
textNameLabel.grid(row=0, column=1, sticky='NSEW', padx=10, pady=10)
textIndexFrame = tk.Frame(textInfoFrame)
textIndexLabel = tk.Message(master=textIndexFrame, anchor=CENTER, justify=CENTER, font=mainfont, width=950)
textIndexLabel.grid(row=0, column=0, sticky='NSEW')
textOutputLabel = tk.Message(master=textIndexFrame, anchor=CENTER, justify=CENTER, font=mainfont, width=950, text='Output Cards: 0')
textOutputLabel.grid(row=1, column=0, sticky='NSEW')

textIndexFrame.grid(row=0, column=2, sticky='NSEW', padx=10, pady=10)

tk.Grid.columnconfigure(textInfoFrame, (0, 2), weight=1, uniform=1)
tk.Grid.columnconfigure(textInfoFrame, 1, weight=2)

translationFrame = tk.ttk.Labelframe(textFrame, text='Translation')
translationFrame.grid(row=1, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.columnconfigure(translationFrame, 0, weight=1)
translationLabel = tk.Label(master=translationFrame, anchor=CENTER, justify=CENTER, font=mainfont, height=4,
                            wraplength=930)
translationLabel.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)

originalFrame = tk.ttk.Labelframe(textFrame, text='Original')
originalFrame.grid(row=2, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.columnconfigure(originalFrame, 0, weight=1)
originalLabel = tk.Label(master=originalFrame, anchor=CENTER, justify=CENTER, font=mainfont, height=4, wraplength=930)
originalLabel.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)

sepTransFrame = tk.ttk.Labelframe(textFrame, text='Individual Translations')
sepTransFrame.grid(row=3, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.columnconfigure(sepTransFrame, 0, weight=1)
sepTransLabel = tk.Label(master=sepTransFrame, anchor=CENTER, justify=CENTER, font=mainfont, height=4, wraplength=930)
sepTransLabel.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)

controlFrame = tk.Frame(textFrame)
tk.Grid.rowconfigure(controlFrame, 0, weight=1)
# tk.Grid.columnconfigure(controlFrame, 0, weight=1)
# tk.Grid.columnconfigure(controlFrame, 1, weight=1)
# tk.Grid.columnconfigure(controlFrame, 2, weight=1)
# tk.Grid.columnconfigure(controlFrame, 3, weight=1)
# tk.Grid.columnconfigure(controlFrame, 4, weight=1)
controlFrame.columnconfigure([0, 1, 2, 3, 4], weight=1, uniform=1)

controlFrame.grid(row=4, column=0, sticky='NSEW', padx=10, pady=10)

revertButton = tk.ttk.Button(controlFrame, text="Revert [1]", command=lambda: handle_keypress('1'))
revertButton.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
replayButton = tk.ttk.Button(controlFrame, text="Replay Voice [q]", command=lambda: handle_keypress('q'))
replayButton.grid(row=0, column=1, sticky='NSEW', padx=10, pady=10)
advanceButton = tk.ttk.Button(controlFrame, text="Advance [space]", command=lambda: handle_keypress(' '))
advanceButton.grid(row=0, column=2, sticky='NSEW', padx=10, pady=10)
ankiButton = tk.ttk.Button(controlFrame, text="Save to Output [4]", command=lambda: handle_keypress('4'))
ankiButton.grid(row=0, column=3, sticky='NSEW', padx=10, pady=10)
gotoButton = tk.ttk.Button(controlFrame, text="Go to index", command=lambda: handle_keypress('5'))
gotoButton.grid(row=0, column=4, sticky='NSEW', padx=10, pady=10)

Menu = tk.Menu(textFrame)
# Menu.add_command(label='Add Text', command=addNewText)
Menu.add_command(label='Edit Config', command=editConfig)
window.config(menu=Menu)

window.bind('<Configure>', resizeLabels)

atlas1 = {'atlas': initializeAtlas()}

window.title("Atlas")


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

    for i in range(10):
        if atlas.currentTrans.ready:
            break
        originalLabel.configure(text="Translating%s" % ('.' * i))
        window.update_idletasks()
        time.sleep(1)

    originalLabel.configure(text="")
    window.update_idletasks()

    print("Showing: %s" % atlas.index)
    translationLabel.configure(text=atlas.currentTrans.translation)
    indexpercent = (atlas.index / len(atlas.sentences) * 100)
    textIndexLabel.configure(text='Index: %s | %.2f%%' % (atlas.index, indexpercent))
    window.update_idletasks()


def showOriginal(atlas):
    originalLabel.configure(text=atlas.currentTrans.original)
    sepTransLabel.configure(text=atlas.currentTrans.separatedTranslation)
    window.update_idletasks()
    atlas.currentTrans.playVoice()


def appendToAnki(atlas):
    with open("Output/Saved Cards - Last Session.txt", 'a', encoding='utf-8') as lastsession, open(
            "Output/Saved Cards - Total.txt", 'a', encoding='utf-8') as total:
        newCard = "\"%s\";\"%s\"\n" % (atlas.currentTrans.translation, atlas.currentTrans.original)
        atlas.newCards += 1
        lastsession.write(newCard)
        total.write(newCard)
    print("Added to deck, %d new cards" % atlas.newCards)
    textOutputLabel.configure(text='Output Cards: %s' % atlas.newCards)


def updateIndex(atlas):
    with open("atlasTextData.json", "r+") as file:
        textData = json.load(file)
        textData[atlas.text]['index'] = atlas.index
        file.truncate(0)
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
    updateIndex(atlas)
    atlas.state = "translation"
    showNewTemplate(atlas)


def playAudio(atlas):
    atlas.currentTrans.playVoice()


window.mainloop()
