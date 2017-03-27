import os
# import xml.etree.ElementTree as ET
from lxml import etree as ET
from lxml import objectify
import chardet


class Book(object):

    amount = 0
    words = []

    def __init__(self, title, author, genre, text):
        self.id = Book.amount
        Book.amount += 1
        self.title = title
        self.author = author
        self.genre = genre
        self.text = text

    def tostring(self):
        i = 'Id: ' + str(self.id) + '\n'
        t = 'Title: ' + self.title + '\n'
        a = 'Author: ' + str(self.author) + '\n'
        g = 'Genre: ' + str(self.genre)
        return i + t + a + g


class Word(object):

    def __init__(self, word, file_id):
        self.word = word
        self.file_id = [file_id]

    def __cmp__(self, other):
        if self.word > other.word:
            return 1
        elif self.word < other.word:
            return -1
        else:
            return 0

    def tostring(self):
        return str(self.word) + ' ' + str(self.file_id)


def make_array(dir):
    result = []
    for name in os.listdir(dir):
        if name == ".DS_Store":
            continue
        else:
            name = 'fb2/' + name
            try:
                temp = open(name, 'r', encoding="utf-8").read().encode('utf-8')
                # print(chardet.detect(temp))
            except UnicodeDecodeError:
                temp = open(name, 'r', encoding="windows-1251").read().encode('utf-8')
                # print(chardet.detect(temp))
            result.append(temp)
    # temp = open('example.fb2', 'r', encoding='utf-8').read().replace('\n', ' ')
    # temp = open('kek.xml', 'r', encoding='utf-8').read()
    result.append(temp)
    return result


def make_obj(files):
    books = []
    ns = {'ns0': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
    for f in files:
        title = ''
        author = {'first-name': '', 'last-name': ''}
        genre = []
        text = ''
        try:
            book = ET.XML(f)
        except ET.XMLSyntaxError:
            parser = objectify.makeparser(huge_tree=True)
            book = objectify.fromstring(f, parser)
        title = book.find('ns0:description/ns0:title-info/ns0:book-title', ns).text
        author['first-name'] = book.find('ns0:description/ns0:title-info/ns0:author/ns0:first-name', ns).text
        author['last-name'] = book.find('ns0:description/ns0:title-info/ns0:author/ns0:last-name', ns).text
        genres = book.findall('ns0:description/ns0:title-info/ns0:genre', ns)
        for g in genres:
            temp = g.text
            temp.encode('utf-8')
            genre.append(temp)
        body = book.find('ns0:body', ns)
        bits_of_text = book.xpath('//text()')
        text = ' '.join(bit.strip() for bit in bits_of_text if bit.strip() != '').lower()
        text = fws(text)
        # text = ET.tostring(body, method='text', encoding='utf-8').decode('utf-8')
        book_obj = Book(title, author, genre, text)
        books.append(book_obj)
    return books


def fws(file):  # file word splitter
    temp = ''
    file.replace('\n', ' ')
    for i in range(len(file)):
        if file[i].isalpha() or file[i] is ' ':
            temp += file[i]
    almoust_result = temp.split(' ')
    result = []
    for w in almoust_result:
        t = Word(w, Book.amount)
        result.append(t)
    return result


def make_ditionary_and_ii(books):
    for b in books:
        t = b.text
        Book.words += t
        Book.words.sort(key=lambda x: x.word)
    res = []
    is_first = True
    for wo in range(len(Book.words)):
        if Book.words[wo].word == '' or Book.words[wo].word == ' ':
            continue
        if is_first:
            res.append(Book.words[wo])
            is_first = False
        else:
            if Book.words[wo] == res[-1]:
                if res[-1].word.file_id != Book.words[wo].word.file_id:
                    res[-1].word.file_id.append(Book.words[wo].word.file_id)
                    res[-1].word.file_id.sort()
                continue
            else:
                res.append(Book.words[wo])
    del res[0]
    print("Dictionary and invert index are created")
    Book.words = res


def main():
    print('Loading...')
    files = make_array('/Users/Greg/PycharmProjects/IR_HW_7/fb2e')
    books = make_obj(files)
    make_ditionary_and_ii(books)
    for i in range(10):
        print(Book.words[i].tostring())


if __name__ == '__main__':
    main()
