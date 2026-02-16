import json
import time
from tkinter import CENTER
import deepl

from langdetect import detect
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import os
import uuid

from Atlas import atlasInfo
from sentenceSegmentation import parse_text_to_sentence

# Prompt the user for a .txt file, convert it for use with the app, and add it to available texts to use
def addNewText():
    filepath = tkFileDialog.askopenfilename(title='New Text Selection', filetypes=[('Text Files', '*.txt')])
    if not os.path.exists(filepath):
        tk.messagebox.showwarning("New Text Selection", "Invalid File Path")
        return
    initialFilePath = 'Converted Texts/'
    os.makedirs(initialFilePath, exist_ok=True)
    fileName = os.path.splitext(os.path.basename(filepath))[0]

    with open(filepath, "r", encoding='utf-8') as file:
        originalText = file.read()

    startIndex = round(len(originalText)/10)
    sampleText = originalText[startIndex:startIndex+300]

    detectedLang = detect(sampleText)

    with open("language Tables/googleTable.json", "r", encoding='utf-8') as file:
        googles = json.load(file)

    result = [None]
    parse_text_to_sentence(originalText, googles[detectedLang], result)
    sentences = result[0]
    sampleSentence = sentences[round(len(sentences)/10)][0:300]

    result = tk.messagebox.askquestion(title="Confirmation",
                                       message="Does the following sentence look correct?\n\n%s\n\nDetected Language: %s" % (
                                       sampleSentence, googles[detectedLang].capitalize()))
    if result != 'yes':
        return

    textInfo = {fileName: {"ID": uuid.uuid1().hex, "index": 0, "lang": googles[detectedLang]}}

    with open("Converted Texts/%s.json" % fileName, "w", encoding='utf-8') as file:
        json.dump(sentences, file, indent=4)

    with open("atlasTextData.json", "a+", encoding='utf-8') as file:
        file.seek(0)
        try:
            jsonData = json.load(file)
        except Exception as e:
            jsonData = {}
        jsonData.update(textInfo)
        file.truncate(0)
        json.dump(jsonData, file, indent=4)

# Create a new config file from the default configs
def newConfig():
    with open("defaultconfig.json", "r", encoding='utf-8') as file:
        config = json.load(file)
    with open('atlasConfig.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)

# Open a GUI for editing various parts of the user config including:
# Native language, DeepL config, and which text is currently activated
# Includes method for the user to add new texts
def editConfig():
    def saveConfig():

        if languageSelector.get() in availableLanguages:
            config['nativelang'] = languageSelector.get().lower()

        if deeplApiEntry.get() != '':
            validation = isValidTranslator(deeplApiEntry.get())
            if validation and deeplApiEntry.get() != config['deeplapikey']:
                tk.messagebox.showinfo("DeepL Validation",
                                       "The inputted DeepL api key is valid, DeepL translation has been enabled")
                config['deeplapikey'] = deeplApiEntry.get()
            elif not validation:
                tk.messagebox.showwarning("DeepL Validation", "The inputted DeepL api key is invalid")
                config['deeplapikey'] = ''

            config['deepl'] = str(validation)

        with open("atlasTextData.json", "r", encoding='utf-8') as file:
            availableTexts = list(json.load(file).keys())

        if textSelector.get() in availableTexts:
            config['currenttext'] = textSelector.get()

        with open("atlasConfig.json", "w", encoding='utf-8') as file:
            json.dump(config, file, indent=4)
        popup.destroy()
        atlas1['atlas'] = initializeAtlas()

    def addTextHelper():
        addTextProgressLabel.configure(text='Converting text...')
        addNewText()
        with open("atlasTextData.json", "r", encoding='utf-8') as file:
            availableTexts = list(json.load(file).keys())
        textSelector['values'] = availableTexts
        if textSelector.get() not in availableTexts and len(availableTexts) > 0:
            textSelector.set('Please select a text.')
        addTextProgressLabel.configure(text='')

    popup = tk.Toplevel(window)
    popup.title('Atlas Config')
    popup.geometry('500x610+%s+%s' % (round(window.winfo_x() + (window.winfo_width() / 4)), window.winfo_y() + 10))
    popup.transient(window)

    with open("atlasConfig.json", "r", encoding='utf-8') as file:
        config = json.load(file)

    with open("Language Tables/combinedTable.json", "r", encoding='utf-8') as file:
        combinedTable = json.load(file)

    availableLanguages = [language.capitalize() for language in list(combinedTable.keys())]

    tk.Grid.columnconfigure(popup, 0, weight=1)

    languageFrame = tk.ttk.Labelframe(popup, text='Please Select Your Native Language')
    tk.Grid.rowconfigure(languageFrame, 0, weight=1)
    tk.Grid.columnconfigure(languageFrame, 0, weight=1)
    languageSelector = tk.ttk.Combobox(languageFrame, values=availableLanguages)

    currentLang = config['nativelang'].capitalize()
    if currentLang in availableLanguages:
        languageSelector.set(currentLang)

    languageSelector.grid(row=0, column=0, sticky='EW', ipadx=10, ipady=10, padx=10, pady=10)
    languageFrame.grid(row=0, column=0, sticky='EW', padx=10, pady=10)

    deeplFrame = tk.ttk.Labelframe(popup, text='DeepL Configuration (Optional)')
    deeplFrame.grid(row=1, column=0, sticky='EW', padx=10, pady=10)
    tk.Grid.columnconfigure(deeplFrame, 0, weight=1)
    tk.Grid.rowconfigure(deeplFrame, 0, weight=1)

    deepllabel = tk.Message(master=deeplFrame, anchor=CENTER, justify=CENTER, width=450,
                            text='DeepL can offer better translations but an API key is required. A free API is available but requires a DeepL account and credit card information.\n If no valid api key is available, Google Translate will be used instead.\nPlease enter a valid DeepL API key.')
    deepllabel.grid(row=0, column=0, sticky='EW', padx=10, pady=10)
    deeplApiEntry = tk.ttk.Entry(deeplFrame)
    deeplApiEntry.insert(0, config['deeplapikey'])
    deeplApiEntry.grid(row=1, column=0, sticky='NSEW', padx=10, pady=10)

    textSelectionFrame = tk.ttk.Labelframe(popup, text='Text Selection')
    textSelectionFrame.grid(row=2, column=0, sticky='EW', padx=10, pady=10)
    tk.Grid.columnconfigure(textSelectionFrame, 0, weight=1)
    tk.Grid.rowconfigure(textSelectionFrame, 0, weight=1)

    addTextLabel = tk.Message(textSelectionFrame, anchor=CENTER, justify=CENTER, width=450,
                              text='A Standard .txt file can be converted for use with this app. Any number of texts can be stored and switched between. The index for each text is unique, you can switch freely between texts without losing your spot. Several sample texts are available in the Atlas folder. A text may take serveral seconds to convert.')
    addTextLabel.grid(row=0, column=0, sticky='EW', padx=10, pady=10)
    addTextButton = tk.ttk.Button(textSelectionFrame, text="Add New Text", command=addTextHelper)
    addTextButton.grid(row=2, column=0, sticky='EW', padx=10, pady=10)
    addTextProgressLabel = tk.ttk.Label(textSelectionFrame, anchor=CENTER, justify=CENTER)
    addTextProgressLabel.grid(row=3, column=0, sticky='EW', padx=10, pady=10)

    with open("atlasTextData.json", "a+", encoding='utf-8') as file:
        file.seek(0)
        try:
            availableTexts = list(json.load(file).keys())
        except:
            availableTexts = []

    textSelector = tk.ttk.Combobox(textSelectionFrame, values=availableTexts)
    if len(availableTexts) == 0:
        textSelector.set("No Texts Available. Add new texts to select.")
    elif config['currenttext'] in availableTexts:
        textSelector.set(config['currenttext'])
    else:
        textSelector.set('Please select a text.')
    textSelector.grid(row=1, column=0, sticky='EW', padx=10, pady=10)

    saveButton = tk.ttk.Button(popup, text="Save Config", command=saveConfig)
    saveButton.grid(row=3, column=0, sticky='NSEW', padx=10, pady=10)

    window.wait_window(popup)

# Returns whether the DeepL api key is valid and ready to use
def isValidTranslator(apikey):
    try:
        deepl.DeepLClient(apikey).get_usage()
        return True
    except:
        return False

# Tries to load user config and creates new one if not available
def loadConfig():
    for i in range(2):
        try:
            # If config doesn't exist create new config
            with open("atlasConfig.json", "r", encoding='utf-8') as file:
                config = json.load(file)
            return config
        except:
            newConfig()

# Prompts the user for an index and goes to that index in the text, if valid
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

# Sets the font size and saves to config file with the inputted number
def setFontSize(newsize):
    mainfont.config(size=newsize)
    with open("atlasConfig.json", "r", encoding='utf-8') as file:
        config = json.load(file)
    config['textsize'] = str(newsize)
    with open('atlasConfig.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)

# When the window is resized, the main text labels are resized to fit
def resizeLabels(event):
    if event.widget == window:
        labels = [translationLabel, originalLabel, sepTransLabel]
        for label in labels:
            label.configure(wraplength=round(event.width * 0.9))

        with open("atlasConfig.json", "r", encoding='utf-8') as file:
            config = json.load(file)
        config['winwidth'] = str(event.width)
        config['winheight'] = str(event.height)
        with open('atlasConfig.json', 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)

# Handles keypresses allowing use of the app with just the keyboard
def handle_keypress(input):
    atlas2 = atlas1['atlas']

    if isinstance(input, str):
        character = input
    else:
        try:
            character = input.char
        except:
            pass
    if character == '3':
        advanceState(atlas2)
    elif character == '2':
        # Replay audio for the current translation
        playAudio(atlas2)
    elif character == '1':
        # Revert the index by 1
        revertOne(atlas2)
    elif character == '4':
        # Add to anki file
        appendToAnki(atlas2)
    elif character == '5':
        # Go to a user inputted index
        gotoIndex(atlas2)
    advanceButton.focus_set()

# Initialize app with info from user config file
def initializeAtlas():
    try:
        # Load Config
        config = loadConfig()

        with open("Output/Saved Cards - Last Session.txt", 'w', encoding='utf-8') as file:
            file.close()
        newAtlas = atlasInfo()

        # Load Text Data
        with open("atlasTextData.json", "r", encoding='utf-8') as file:
            textData = json.load(file)
        currentText = (config['currenttext'], textData[config['currenttext']])

        configfontsize = config['textsize']
        fontsizevar.set(configfontsize)
        setFontSize(configfontsize)

        window.geometry('%sx%s' % (config['winwidth'], config['winheight']))

        newAtlas.text = currentText[0]
        newAtlas.index = max(currentText[1]['index'] - 1, -1)

        # Load Language Table
        with open("Language Tables/combinedTable.json", "r", encoding='utf-8') as file:
            combinedTable = json.load(file)

        newAtlas.initializeTranslator(combinedTable[currentText[1]['lang']],
                                      combinedTable[config['nativelang']], config['deepl'],
                                      config['deeplapikey'])


        with open('Converted Texts/%s.json' % config['currenttext'], 'r', encoding='utf-8') as file:
            newAtlas.sentences = json.load(file)


        window.bind("<Key>", handle_keypress)



        translationLabel.configure(text="Welcome to Atlas")
        originalLabel.configure(text="Advance to continue")
        sepTransLabel.configure(text='')
        textNameLabel.configure(text=newAtlas.text)
        indexpercent = ((max(newAtlas.index,0)) / max((len(newAtlas.sentences)-1),1) * 100)
        textIndexLabel.configure(text='Index: %s | %.2f%%' % (max(newAtlas.index,0), indexpercent))



        return newAtlas
    except Exception as e:
        print(e)
        translationLabel.configure(text="Welcome to Atlas")
        originalLabel.configure(text="No text selected")
        sepTransLabel.configure(text='Texts can be added and selected in the configuration menu')
        pass

window = tk.Tk()

mainfont = tkFont.Font(family='Arial', size=15)

tk.Grid.columnconfigure(window, 0, weight=1)
tk.Grid.rowconfigure(window, 0, weight=1)

textFrame = tk.Frame(master=window)
tk.Grid.columnconfigure(textFrame, 0, weight=1)
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
textOutputLabel.bind("<Button-1>", lambda e: os.startfile('Output'))

textIndexFrame.grid(row=0, column=2, sticky='NSEW', padx=10, pady=10)

tk.Grid.columnconfigure(textInfoFrame, (0, 2), weight=1, uniform=1)
tk.Grid.columnconfigure(textInfoFrame, 1, weight=2)

translationFrame = tk.ttk.Labelframe(textFrame, text='Translation')
translationFrame.grid(row=1, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.columnconfigure(translationFrame, 0, weight=1)
translationLabel = tk.Label(master=translationFrame, anchor=tk.CENTER, justify=tk.CENTER, font=mainfont,
                            wraplength=930)
translationLabel.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.rowconfigure(translationFrame, 0, weight=1)

originalFrame = tk.ttk.Labelframe(textFrame, text='Original')
originalFrame.grid(row=2, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.columnconfigure(originalFrame, 0, weight=1)
originalLabel = tk.Label(master=originalFrame, anchor='center', justify='center', font=mainfont, wraplength=930)
originalLabel.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.rowconfigure(originalFrame, 0, weight=1)

sepTransFrame = tk.ttk.Labelframe(textFrame, text='Individual Translations')
sepTransFrame.grid(row=3, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.columnconfigure(sepTransFrame, 0, weight=1)
sepTransLabel = tk.Label(master=sepTransFrame, anchor=CENTER, justify=CENTER, font=mainfont, wraplength=930)
sepTransLabel.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
tk.Grid.rowconfigure(sepTransFrame, 0, weight=1)

controlFrame = tk.Frame(textFrame)
tk.Grid.rowconfigure(controlFrame, 0, weight=1)
controlFrame.columnconfigure([0, 1, 2, 3, 4], weight=1, uniform=1)

controlFrame.grid(row=4, column=0, sticky='NSEW', padx=10, pady=10)

revertButton = tk.ttk.Button(controlFrame, text="Revert [1]", command=lambda: handle_keypress('1'))
revertButton.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
replayButton = tk.ttk.Button(controlFrame, text="Replay Voice [2]", command=lambda: handle_keypress('2'))
replayButton.grid(row=0, column=1, sticky='NSEW', padx=10, pady=10)
advanceButton = tk.ttk.Button(controlFrame, text="Advance [3]", command=lambda: handle_keypress('3'))
advanceButton.grid(row=0, column=2, sticky='NSEW', padx=10, pady=10)
ankiButton = tk.ttk.Button(controlFrame, text="Save to Output [4]", command=lambda: handle_keypress('4'))
ankiButton.grid(row=0, column=3, sticky='NSEW', padx=10, pady=10)
gotoButton = tk.ttk.Button(controlFrame, text="Go to index [5]", command=lambda: handle_keypress('5'))
gotoButton.grid(row=0, column=4, sticky='NSEW', padx=10, pady=10)

advanceButton.focus_set()

Menu = tk.Menu(textFrame)
# Menu.add_command(label='Add Text', command=addNewText)
Menu.add_command(label='Edit Config', command=editConfig)
window.config(menu=Menu)

window.bind('<Configure>', resizeLabels)

window.geometry("700x700")

atlas1 = {'atlas': initializeAtlas()}

window.title("Atlas")

# Clears text labels and shows the next index in the text, initiates translations
def showNewTemplate(atlas):

    try:
        atlas.currentTrans.stopVoice()
    except:
        pass

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



    originalLabel.configure(text="")
    translationLabel.configure(text="")
    sepTransLabel.configure(text="")

    if atlas.index >= len(atlas.sentences):
        atlas.state = 'disabled'
        translationLabel.configure(text="This end of this text has been reached")
        originalLabel.configure(text="A new text can be selected in the config menu")
        return

    for i in range(20):
        if atlas.currentTrans.ready:
            break
        originalLabel.configure(text="Translating%s" % ('.' * i))
        window.update_idletasks()
        time.sleep(1)

    originalLabel.configure(text="")
    window.update_idletasks()

    translationLabel.configure(text=atlas.currentTrans.translation)
    indexpercent = (atlas.index / max((len(atlas.sentences)-1),1) * 100)
    textIndexLabel.configure(text='Index: %s | %.2f%%' % (atlas.index, indexpercent))
    window.update_idletasks()

# Shows original text from selected text, as well as individual translations for each word
def showOriginal(atlas):
    originalLabel.configure(text=atlas.currentTrans.original)
    sepTransLabel.configure(text=atlas.currentTrans.separatedTranslation)
    window.update_idletasks()
    atlas.currentTrans.playVoice()

# Adds the original text and its translation to a file that is easily inputted into Anki, adds to backup file as well
def appendToAnki(atlas):
    with open("Output/Saved Cards - Last Session.txt", 'a', encoding='utf-8') as lastsession, open(
            "Output/Saved Cards - Total.txt", 'a', encoding='utf-8') as total:
        newCard = "\"%s\";\"%s\"\n" % (atlas.currentTrans.translation, atlas.currentTrans.original)
        atlas.newCards += 1
        lastsession.write(newCard)
        total.write(newCard)
    textOutputLabel.configure(text='Output Cards: %s' % atlas.newCards)

# Updates the index for the current text in the atlasTextData.json file
def updateIndex(atlas):
    with open("atlasTextData.json", "r+", encoding='utf-8') as file:
        textData = json.load(file)
        textData[atlas.text]['index'] = atlas.index
        file.truncate(0)
        file.seek(0)
        json.dump(textData, file, indent=4)

# Advances state of the app, showing the original text if translation is shown,
# and showing a new translation if the current index is finished
def advanceState(atlas):
    if atlas.state == "translation":
        atlas.state = "original"
        showOriginal(atlas)
    elif atlas.state == "original":
        atlas.state = "translation"
        atlas.index += 1
        updateIndex(atlas)
        showNewTemplate(atlas)

# Goes back 1 in the index, showing the previous translation
def revertOne(atlas):
    atlas.index -= 1
    atlas.transQueue.appendleft(atlas.currentTrans)
    atlas.addTranslationByIndex(atlas.index, 'left')
    updateIndex(atlas)
    atlas.state = "translation"
    showNewTemplate(atlas)

# Plays the audio of the current translation
def playAudio(atlas):
    atlas.currentTrans.playVoice()


window.mainloop()
