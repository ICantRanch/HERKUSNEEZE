import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

book = epub.read_epub('C:/Users/Hubert/Desktop/Inspo/HPPL1.epub')
bookitems = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
print(bookitems[2].get_name())





chapters = [item for item in bookitems if 'Chapter' in item.get_name()]

# chosen = chapters[1]
# soup = BeautifulSoup(chosen.get_body_content(), 'html.parser')
# paragraphs = soup.find_all('div', 'row')
#
# text = paragraphs[3].get_text()
#
# text = [paragraph.get_text() for paragraph in soup.find_all('div class row')]
# result = ' '.join(text)


pass
def chapterToStr(chapter):
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
    text = [paragraph.get_text() for paragraph in soup.find_all('div', 'row')]
    return ' '.join(text)

texts = {}
for chapter in chapters:
    texts[chapter.get_name()] = chapterToStr(chapter)
pass

chapterParas = {}
for name, text in texts.items():
    chapterParas[name] = text.splitlines()
    chapterParas[name] = list(filter(lambda line: len(line) > 1, chapterParas[name]))
    for index, para in enumerate(chapterParas[name]):
        while not para.startswith('\t') and index > 1 and index < len(chapterParas[name]):
            del chapterParas[name][index]
            chapterParas[name][index-1] = chapterParas[name][index-1] + " " + para
            if index < len(chapterParas[name]):
                para = chapterParas[name][index]
    #while paragraph doesnt start with \t\t, append paragraph to previos



for name, chapter in chapterParas.items():
    for i, para in enumerate(chapter):

        # chapterParas[name][i] = re.split(r"\.\s*", para)
        chapterParas[name][i] = re.split('(?<=[.!?]) +', para)
        for index, line in enumerate(chapterParas[name][i]):
            while line.endswith("Mr.") or line.endswith("Mrs.") or line.endswith("Ms."):
                temp = line
                del chapterParas[name][i][index]
                chapterParas[name][i][index] = temp + " " + chapterParas[name][i][index]
                line = chapterParas[name][i][index]
                pass
        chapterParas[name][i] = list(filter(lambda line: len(line) > 1, chapterParas[name][i]))
print(repr(texts['Text/Chapter01.xhtml']))
pass