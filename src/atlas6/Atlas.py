# This is a sample Python script.
import collections
import threading
from tempfile import NamedTemporaryFile

from playsound3 import playsound
from gtts import gTTS
import deepl
from deep_translator import GoogleTranslator


# Load Config

class atlasInfo:
    QUEUE_MAXLEN = 5

    def __init__(self):
        self.text = None
        self.newCards = 0
        self.index = None
        self.sentences = None
        self.transObj = None
        self.transQueue = collections.deque(maxlen=self.QUEUE_MAXLEN)
        self.currentTrans = None
        self.translationLabel = None
        self.originalLabel = None
        self.sepTransLabel = None
        self.state = 'original'

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
            try:
                playsound(self.voice.name, block=False)
            except Exception as e:
                return

    class translatorObj:
        def __init__(self, transType, translator, source_langs, target_langs):
            self.targetLangs = target_langs
            self.sourceLangs = source_langs
            self.translator = translator
            self.transType = transType

    def initializeTranslator(self, sources, targets, isdeepl, key):
        try:
            if isdeepl:
                deeplTranslator = deepl.DeepLClient(key)
                deeplTranslator.get_usage()
                self.transObj = self.translatorObj('deepl', deeplTranslator, sources, targets)
            else:
                raise Exception
        except:
            googleTranslator = GoogleTranslator(source='auto', target=targets['google'])
            self.transObj = self.translatorObj('google', googleTranslator, sources, targets)

    def translate(self, texts):
        if self.transObj.transType == 'google':
            try:
                # Don't judge this too much, this cludge is because the translation library
                # doesn't like multiple threads using the same translator :/
                googleTranslator = GoogleTranslator(source='auto', target=self.transObj.targetLangs['google'])

                if isinstance(texts, list):
                    results = self.transObj.translator.translate_batch(texts)
                    output = " | ".join([result for result in results if isinstance(result, str)])
                    return output
                else:
                    result = googleTranslator.translate(texts)
                    if len(result) < 1:
                        raise Exception("Invalid Translation")
                    return result
            except Exception as e:
                print('Translation Exception' + str(e))
                return "Error in Translation"
        elif self.transObj.transType == 'deepl':
            try:
                results = self.transObj.translator.translate_text(text=texts, target_lang=self.transObj.targetLangs['deepl'])
                if isinstance(results, list):
                    return " | ".join([result.text for result in results])
                else:
                    return results.text
            except Exception as e:
                print('Translation Exception' + str(e))
                return "Error in Translation"
        else:
            raise Exception("Invalid Translator Type")

    def translateVoice(self, text):
        try:
            voiceMp3 = NamedTemporaryFile()
            gTTS(text=text, lang=self.transObj.sourceLangs['google']).write_to_fp(voiceMp3)
            return voiceMp3
        except:
            return None

    def populateTranslation(self, sentenceTrans):
        sentenceTrans.translation = self.translate(sentenceTrans.original)
        sentenceTrans.separatedTranslation = self.translate(sentenceTrans.original.split())
        sentenceTrans.voice = self.translateVoice(sentenceTrans.original)
        sentenceTrans.ready = True

    def addTranslationByIndex(self, index, mode):
        if 0 <= index < len(self.sentences):
            newTrans = self.sentenceTranslation(index, self.sentences[index])
        else:
            return
        if mode == 'left':
            self.transQueue.appendleft(newTrans)
        elif mode == 'right':
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
            if lastIndex+1 >= len(self.sentences):
                return
            self.addTranslationByIndex(lastIndex + 1, 'right')

    def playAudio(self):
        # playsound("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/voice.mp3")
        if self.currentTrans.voice is not None:
            self.playVoice(self.currentTrans.voice)
