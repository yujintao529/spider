# -*- coding: UTF-8 -*-

import ssl
import traceback
import urllib.request
import threadpool
from util import debug

from bs4 import BeautifulSoup
import disk

_context = ssl._create_unverified_context()
_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3;Win64; x64) AppleWebKit/537.36(KHTML, '
                          'like Gecko)Chrome/48.0.2564.48 Safari/537.36'}

pool = threadpool.ThreadPool(8)


def chapter_disk_handler(chapter, parent_path, file_name):
    file = disk.note_file(parent_path, file_name)
    disk.note_to_disk(file, chapter.content)
    return file


class Engine(object):

    def execute(self):
        pass




class ResolveEngine(Engine):

    def __init__(self, content):
        self.content = content
        self.soup = BeautifulSoup(self.content, features="html.parser")


class LoadEngine(Engine):

    def __init__(self, url, headers=_headers, context=_context, charset="gbk"):
        self.headers = headers
        self.context = context
        self.url = url
        self.charset = charset

    def execute(self):
        try:
            request = urllib.request.Request(url=self.url, headers=self.headers)
            response = urllib.request.urlopen(url=request, context=self.context)
            result = response.read().decode(self.charset)
            debug("load success : " + self.url)
        except Exception:
            print("loadEngine Error " + self.url)
            traceback.print_exc()
        return result


class Note(object):

    def __init__(self, title):
        self.title = title
        self.chapters = list()
        # 数据库使用
        self.id = -1
        self.create_time = None

    def __str__(self):
        strs = list()
        strs.append(self.title)
        strs.append("\n")
        for inx, chapter in self.chapters:
            strs.append(chapter).append("\n")
        return "".join(strs)

    def simple_str(self):
        return self.title + "[" + str(self.id) + "-" + str(len(self.chapters)) + "]"


class Chapter(object):
    def __init__(self, title, num=-1, content=None):
        self.title = title
        self.num = num
        self.content = content

    def __str__(self):
        return self.num, ".", self.title, "-", self.content.substring[0, 20]

    def inject(selff):


class UrlChapter(Chapter):
    def __init__(self, url, title, file=None, num=-1, content=None):
        super().__init__(title, num, content)
        self.url = url
        self.file = file
