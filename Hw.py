import os
# import xml.etree.ElementTree as ET
from lxml import etree as et
from lxml import objectify
from chardet.universaldetector import UniversalDetector


class Book(object):
    amount = 0
    words = []
    titles = []
    authors = []
    genres = []

    def __init__(self, title, author, genre, text):
        self.id = Book.amount
        Book.amount += 1
        self.title = title
        self.author = author
        self.genre = genre
        self.text = text
        Book.titles.append(Title(self.title, self.id))
        Book.authors.append(Author(self.author, self.id))
        Book.genres.append(Genre(self.genre, self.id))

    def tostring(self):
        i = 'Id: ' + str(self.id) + '\n'
        t = 'Title: ' + self.title + '\n'
        a = 'Author: ' + str(self.author) + '\n'
        g = 'Genre: ' + str(self.genre)
        return i + t + a + g


class Word(object):
    amount = 0

    def __init__(self, word, file_id):
        Word.amount += 1
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


class Author(object):
    def __init__(self, author, id):
        self.author = author
        self.id = id


class Title(object):
    def __init__(self, title, id):
        self.title = title
        self.id = id


class Genre(object):
    def __init__(self, genre, id):
        self.genre = genre
        self.id = id


class Score(object):
    def __init__(self, score, id):
        self.score = score
        self.id = id


def make_array(dir):
    result = []
    detector = UniversalDetector()
    counter = 0
    for name in os.listdir(dir):
        if name == ".DS_Store":
            continue
        else:
            counter += 1
            name = 'fb2/' + name
            temp = open(name, 'rb')
            detector.reset()
            for line in temp.readlines():
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
            print(str(counter) + ') ' + str(detector.result))
            temp = open(name, 'rb').read().decode(detector.result['encoding'])
            result.append(bytes(temp, encoding=detector.result['encoding']))
    # temp = open('example.fb2', 'r', encoding='utf-8').read().replace('\n', ' ')
    # temp = open('kek.xml', 'r', encoding='utf-8').read()
    # result.append(temp)
    return result


def make_obj(files):
    books = []
    ns = {'ns0': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
    parser = objectify.makeparser(huge_tree=True)
    for f in files:
        author = {'first-name': '', 'last-name': ''}
        genre = []
        try:
            book = et.XML(f)
        except et.XMLSyntaxError:
            book = objectify.fromstring(f, parser)
        title_info = book.find('ns0:description/ns0:title-info', ns)
        title = title_info.find('ns0:book-title', ns).text
        author['first-name'] = title_info.find('ns0:author/ns0:first-name', ns).text
        author['last-name'] = title_info.find('ns0:author/ns0:last-name', ns).text
        genres = title_info.findall('ns0:genre', ns)
        for g in genres:
            temp = g.text
            genre.append(temp)
        # body = book.find('ns0:body', ns)
        bits_of_text = book.xpath('//text()')
        text = ' '.join(bit.strip() for bit in bits_of_text if bit.strip() != '').lower()
        text = fws(text)
        # text = ET.tostring(body, method='text', encoding='utf-8').decode('utf-8')
        book_obj = Book(title, author, genre, text)
        books.append(book_obj)
        print('Books added: {}'.format(Book.amount))
        print(book_obj.tostring())
        print()
    print('Books are objectified')
    return books


def fws(file):  # file word splitter
    temp = ''
    file.replace('\n', ' ')
    for i in range(len(file)):
        if file[i].isalpha() or file[i] is ' ':
            temp += file[i]
    almost_result = temp.split(' ')
    result = []
    for w in almost_result:
        if len(w) > 20:
            continue
        else:
            t = Word(w, Book.amount)
            result.append(t)
    return result


def make_dictionary_and_ii(books):
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
            if Book.words[wo].word == res[-1].word:
                if res[-1].file_id not in Book.words[wo].file_id:
                    for id in Book.words[wo].file_id:
                        if id not in res[-1].file_id:
                            res[-1].file_id.append(id)
                    res[-1].file_id.sort()
                continue
            else:
                res.append(Book.words[wo])
    del res[0]
    print("Dictionary and invert index are created")
    Book.words = res


def check_title_zone(query, id):
    title = Book.titles[id].title.split(' ')
    for t in title:
        if t in query:
            return 1
    return 0


def check_author_zone(query, id):
    author = Book.authors[id].author
    for a in author:
        if a in query:
            return 1
    return 0


def check_genre_zone(query, id):
    genre = Book.genres[id].genre
    for g in genre:
        if g in query:
            return 1
    return 0


def check_text_zone(query):
    result = []
    for q in query:
        for w in Book.words:
            if q == w.word:
                result += w.file_id
    return result


def score_query(query, id, text_ids):
    title = check_title_zone(query, id)
    author = check_author_zone(query, id)
    genre = check_genre_zone(query, id)
    if id in text_ids:
        text = 1
    else:
        text = 0
    return author * 0.2 + title * 0.2 + genre * 0.1 + text * 0.5


def check_all_index(query):
    score = []
    query = query.split(' ')
    text_ids = check_text_zone(query)
    for i in range(Book.amount):
        score.append(Score(score_query(query, i, text_ids), i))
    return score


def top_books(query):
    result = []
    scores = check_all_index(query)
    scores.sort(key=lambda x: x.score)
    for i in range(10):
        if scores[i].score == 0:
            continue
        else:
            result.append(scores[i].id)
    return result


def main():
    print('Loading...')
    files = make_array('/Users/Greg/PycharmProjects/IR_HW_7/fb2e')
    books = make_obj(files)
    make_dictionary_and_ii(books)
    while True:
        print('Enter your query: ')
        query = input().lower()
        res = top_books(query)
        print(res)


if __name__ == '__main__':
    main()
