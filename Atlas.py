# This is a sample Python script.
import collections
import threading
from tempfile import NamedTemporaryFile

from playsound3 import playsound
from gtts import gTTS



# Load Config

class atlasInfo:
    QUEUE_MAXLEN = 5

    def __init__(self):
        self.newCards = None
        self.index = None
        self.sentences = None
        self.transObj = None
        self.transQueue = collections.deque(maxlen=self.QUEUE_MAXLEN)
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

        def playVoice(self):
            playsound(self.voice.name, block=False)

    class translatorObj:
        def __init__(self, transType, translator, source_lang, target_lang):
            self.targetLang = target_lang
            self.sourceLang = source_lang
            self.translator = translator
            self.transType = transType

    def translate(self, text):
        if self.transObj.transType == 'google':
            try:
                return self.transObj.translator.translate(text=text)
            except:
                return "Error in Translation"
        elif self.transObj.transType == 'deepl':
            try:
                results = self.transObj.translator.translate_text(text=text, target_lang=self.transObj.targetLang)
                if isinstance(results, list):
                    return " | ".join([result.text for result in results])
                else:
                    return results.text
            except:
                return "Error in Translation"
        else:
            raise Exception("Invalid Translator Type")

    def translateVoice(self, text):
        voiceMp3 = NamedTemporaryFile()
        gTTS(text=text, lang=self.transObj.sourceLang).write_to_fp(voiceMp3)
        return voiceMp3

    def populateTranslation(self, sentenceTrans):
        sentenceTrans.translation = self.translate(sentenceTrans.original)
        sentenceTrans.separatedTranslation = self.translate(sentenceTrans.original.split())
        sentenceTrans.voice = self.translateVoice(sentenceTrans.original)
        sentenceTrans.ready = True

    def addTranslationByIndex(self, index, mode):
        newTrans = self.sentenceTranslation(index, self.sentences[index])
        if mode == 'left':
            print("adding left")
            self.transQueue.appendleft(newTrans)
        elif mode == 'right':
            print("adding right")
            self.transQueue.append(newTrans)
        else:
            raise Exception("Invalid append mode")
        x = threading.Thread(target=self.populateTranslation, args=[newTrans], daemon=True)
        x.start()

    def fillQueue(self):
        if len(self.transQueue) == 0:
            self.addTranslationByIndex(self.index, 'right')
        while len(self.transQueue) < self.transQueue.maxlen:
            lastElement = self.transQueue.pop()
            lastIndex = lastElement.index
            self.transQueue.append(lastElement)
            self.addTranslationByIndex(lastIndex + 1, 'right')

    def playAudio(self):
        # playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
        self.playVoice(self.currentTrans.voice)
