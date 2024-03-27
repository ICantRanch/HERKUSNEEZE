# This is a sample Python script.
import pickle
from tkinter import END, CENTER

import pandas
from deep_translator import GoogleTranslator
import re
from playsound import playsound
from gtts import gTTS
import tkinter as tk
import os

#Initialize and shift files
if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards - Depreciated.txt"):
    os.remove("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards - Depreciated.txt")
if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards.txt"):
    old_file = os.path.join("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/", "Buy New Cards.txt")
    new_file = os.path.join("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/", "Buy New Cards - Depreciated.txt")
    os.rename(old_file, new_file)

#Read document with sentences
data = pandas.read_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/BaskervillesHorror.tsv", header=0, index_col=0,
                       sep='\t')
#Isolate sentences and initalize state
print(data)
sentences = data["Sentence"]
print(sentences)
index = None
newCards = 0
state = "original"

#Initialzie index variable from file
with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'rb') as file:
    index = pickle.load(file)
print("Index: " + str(index))

#Initalize google translator
translator = GoogleTranslator(source='polish', target='english')

original = translation = sepTrans = None


def showNewTemplate():
    global index, translator, translation, original, sepTrans, translationLabel, originalLabel, sepTransLabel, window

    translationLabel.configure(text = "")
    originalLabel.configure(text = "")
    sepTransLabel.configure(text = "")
    window.update_idletasks()

    original = sentences[index]

    # while len(original) > 60:
    #     print("Skipped Sentence")
    #     index += 1
    #     original = sentences[index]
    translation = translator.translate(text=original)

    translationLabel.configure(text = translation)
    window.update_idletasks()

    if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3"):
        os.remove("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
    voice = gTTS(text=original, lang='pl', slow=False)
    voice.save("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")

    nopunc = re.sub(r'[^\w\s]', '', original)
    nopunc = nopunc.split()
    nopunc = [word for word in nopunc if not word.isnumeric()]
    try:
        transwords = translator.translate_batch(nopunc)
    except:
        transwords = ['Error in Translation']
    sepTrans = " ".join(transwords)


def showOriginal():
    global index, original, originalLabel, window, sepTrans
    originalLabel.configure(text =  original)
    sepTransLabel.configure(text =  sepTrans)
    window.update_idletasks()
    playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
    index += 1
    with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'wb') as file:
        pickle.dump(index, file)


def appendToAnki():
    global original, translation, newCards
    with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards.txt", 'a', encoding='utf-8') as deck:
        newCard = "%s;%s\n"%(translation, original)
        newCards += 1
        deck.write(newCard)
    print("Added to deck, %d new cards" %newCards)


def advanceState():
    global state
    if state == "translation":
        state = "original"
        showOriginal()
    else:
        state = "translation"
        showNewTemplate()

def revertOne():
    global index, state

    index -= 1
    if state == "original":
        index -= 1
    showNewTemplate()
    state = "translation"

def playAudio():
    playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")

def handle_keypress(event):
    if event.char == ' ':
        advanceState()
        return
    elif event.char == 'q':
        # Replay audio
        playAudio()
        return
    elif event.char == '1':
        revertOne()
        return
    elif event.char == '2':
        return
    elif event.char == '3':
        return
    elif event.char == '4':
        # Add to anki file
        appendToAnki()
        return


window = tk.Tk()
textFrame = tk.Frame(master=window, width=200, height=100, bg="red")
textFrame.pack(fill=tk.BOTH, expand=True)
# translationLabel = tk.Label(master=textFrame, text='it me', font=("Arial", 25))
translationLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
#translationLabel.configure(text = "it me")
translationLabel.configure(text = "it me and I feel as though there must be some kind of way out of here")
translationLabel.pack(fill=tk.X)
# originalLabel = tk.Label(master=textFrame, font=("Arial", 25))
originalLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
originalLabel.pack(fill=tk.X)
# sepTransLabel = tk.Label(master=textFrame, font=("Arial", 25))
sepTransLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
sepTransLabel.pack(fill=tk.X)
textFrame.pack()
window.geometry("1000x300")
window.bind("<Key>", handle_keypress)
window.title("HERKUSNEEZE")
window.mainloop()
