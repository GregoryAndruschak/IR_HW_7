import os
# import xml.etree.ElementTree as ET
from lxml import etree as ET
from lxml import objectify
import chardet


class Book(object):

    amount = 0

    def __init__(self, title, author, genre):
        self.id = Book.amount
        Book.amount += 1
        self.title = title
        self.author = author
        self.genre = genre

    def tostring(self):
        i = 'Id: ' + str(self.id) + '\n'
        t = 'Title: ' + self.title + '\n'
        a = 'Author: ' + str(self.author) + '\n'
        g = 'Genre: ' + str(self.genre)
        return i + t + a + g


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
        title.encode('utf-8')
        author['first-name'] = book.find('ns0:description/ns0:title-info/ns0:author/ns0:first-name', ns).text
        author['first-name'].encode('utf-8')
        author['last-name'] = book.find('ns0:description/ns0:title-info/ns0:author/ns0:last-name', ns).text
        author['last-name'].encode('utf-8')
        genres = book.findall('ns0:description/ns0:title-info/ns0:genre', ns)
        for g in genres:
            temp = g.text
            temp.encode('utf-8')
            genre.append(temp)
        body = book.find('ns0:body', ns)
        bits_of_text = book.xpath('//text()')
        text = ' '.join(bit.strip() for bit in bits_of_text if bit.strip() != '')
        text.encode('utf-8')
        # text = ET.tostring(body, method='text', encoding='utf-8').decode('utf-8')
        book_obj = Book(title, author, genre)
        books.append(book_obj)
        print(book_obj.tostring())
        print()
    print(Book.amount)



def main():
    files = make_array('/Users/Greg/PycharmProjects/IR_HW_7/fb2e')
    make_obj(files)


if __name__ == '__main__':
    main()
