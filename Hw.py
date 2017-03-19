import os
from lxml import etree


class Book(object):
    def __init__(self, name, author, genre, text):
        self.name = name
        self.author = author
        self.genre = genre
        self.text = text


def make_array(dir):
    result = []
    for name in os.listdir(dir):
        if name == ".DS_Store":
            continue
        else:
            name = 'fb2/' + name
            try:
                temp = open(name, 'r', encoding="utf-8").read()
                temp = bytearray(temp, encoding='utf-8')
            except UnicodeDecodeError:
                temp = open(name, 'r', encoding="windows-1251").read().encode(encoding='utf-8')
                temp = bytearray(temp, encoding='utf-8')
            result.append(temp)
    return result


def make_obj(files):
    for f in files:
        book = etree.XML(f)
        name = book.tag
        print(name)


def main():
    files = make_array('/Users/Greg/PycharmProjects/IR_HW_7/fb2')
    make_obj(files)


main()
