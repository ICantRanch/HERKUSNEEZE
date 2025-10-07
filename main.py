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

class atlasInfo:
    def __init__(self):
        self.newCards = None
        self.index = None
        self.translator = None
        self.translation = None
        self.original = None
        self.sepTrans = None
        self.translationLabel = None
        self.originalLabel = None
        self.sepTransLabel = None
        self.window = None
        self.state = None

atlas1 = atlasInfo()

#Initialize and shift files
if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards - Depreciated.txt"):
    os.remove("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards - Depreciated.txt")
if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards.txt"):
    old_file = os.path.join("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/", "Buy New Cards.txt")
    new_file = os.path.join("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/", "Buy New Cards - Depreciated.txt")
    os.rename(old_file, new_file)

#Read document with sentences
data = pandas.read_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Kongres futurologiczny.tsv", header=0, index_col=0,
                       sep='\t')
#Isolate sentences and initalize state
print(data)
sentences = data["Sentence"]
print(sentences)
atlas1.index = None
atlas1.newCards = 0
atlas1.state = "original"
#original = translation = sepTrans = None

#Initialzie index variable from file
with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'rb') as file:
    atlas1.index = pickle.load(file)
print("Index: " + str(atlas1.index) + " " + str('%.2f' % ((atlas1.index/len(sentences))*100)) + "%")

#Initalize google translator
atlas1.translator = GoogleTranslator(source='polish', target='english')

atlas1.window = tk.Tk()
textFrame = tk.Frame(master=atlas1.window, width=200, height=100, bg="red")
textFrame.pack(fill=tk.BOTH, expand=True)
# translationLabel = tk.Label(master=textFrame, text='it me', font=("Arial", 25))
atlas1.translationLabel = tk.Message(master=textFrame, justify=CENTER, font=("Arial", 25), width=1000)
#translationLabel.configure(text = "it me")
atlas1.translationLabel.configure(text = "it me")
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


#atlas1 = atlasInfo(index, translator, translation, original, sepTrans, translationLabel, originalLabel, sepTransLabel, window, newCards)
def showNewTemplate(atlas):
    #global index, translator, translation, original, sepTrans, translationLabel, originalLabel, sepTransLabel, window

    atlas.translationLabel.configure(text = "")
    atlas.originalLabel.configure(text = "Translating...")
    atlas.sepTransLabel.configure(text = "")
    atlas.window.update_idletasks()

    atlas.original = sentences[atlas.index]

    # while len(original) > 60:
    #     print("Skipped Sentence")
    #     index += 1
    #     original = sentences[index]
    atlas.translation = atlas.translator.translate(text=atlas.original)

    atlas.translationLabel.configure(text = atlas.translation)
    atlas.window.update_idletasks()

    if os.path.isfile("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3"):
        os.remove("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
    voice = gTTS(text=atlas.original, lang='pl', slow=False)
    voice.save("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
    
    nopunc = re.sub(r'[^\w\s]', '', atlas.original)
    nopunc = nopunc.split()
    nopunc = [word for word in nopunc if not word.isnumeric()]
    try:
        transwords = atlas.translator.translate_batch(nopunc)
    except:
        transwords = ['Error in Translation']
    sepTrans = " ".join(transwords)

    atlas.originalLabel.configure(text="")

def showOriginal(atlas):
    #global index, original, originalLabel, window, sepTrans
    atlas.originalLabel.configure(text=atlas.original)
    atlas.sepTransLabel.configure(text=atlas.sepTrans)
    atlas.window.update_idletasks()
    playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3", False)
    atlas.index += 1
    with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Vars-HKSZ", 'wb') as file:
        pickle.dump(atlas.index, file)


def appendToAnki(atlas):
    #global original, translation, newCards

    with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/Buy New Cards.txt", 'a', encoding='utf-8') as deck:
        newCard = "%s;%s\n"%(atlas.translation, atlas.original)
        atlas.newCards += 1
        deck.write(newCard)
    print("Added to deck, %d new cards" %atlas.newCards)


def advanceState(atlas):
    if atlas.state == "translation":
        atlas.state = "original"
        showOriginal(atlas)
    else:
        atlas.state = "translation"
        showNewTemplate(atlas)

def revertOne(atlas):
    #global index, state

    atlas.index -= 1
    if atlas.state == "original":
        atlas.index -= 1
    showNewTemplate(atlas)
    atlas.state = "translation"

def playAudio():
    playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")

def handle_keypress(event):
    if event.char == ' ':
        advanceState(atlas1)
        return
    elif event.char == 'q':
        # Replay audio
        playAudio()
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
        appendToAnki()
        return

atlas1.window.bind("<Key>", handle_keypress)
atlas1.window.mainloop()