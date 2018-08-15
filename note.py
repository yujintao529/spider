# -*- coding: UTF-8 -*-

import ssl
import traceback
import urllib.request
import threadpool
import log
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


def is_normal(state):
    return state == 1000


def is_error(state):
    return state == 9999


def is_never(state):
    return state == 0


class Engine(object):

    def execute(self):
        pass

    def exit(self):
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
        result = None
        try:
            request = urllib.request.Request(url=self.url, headers=self.headers)
            response = urllib.request.urlopen(url=request, context=self.context)
            result = response.read().decode(self.charset,'ignore')
            log.debug("LoadEngine http load success  " + self.url)
        except Exception:
            print("LoadEngine http load error " + self.url)
            traceback.print_exc()
        return result


class Note(object):

    def __init__(self, title):
        self.chapters = list()
        self.title = title
        self.id = -1
        self.create_time = None

    def __str__(self):
        strs = list()
        strs.append(self.title)
        strs.append("\n")
        for inx, chapter in self.chapters:
            strs.append(chapter).append("\n")
        return "".join(strs)

    def inject(self, result_dic):
        if result_dic is not None:
            self.id = result_dic['id']
            self.create_time = result_dic['create_time']
            self.title = result_dic['title']

    def simple_str(self):
        return self.title + "[" + str(self.id) + "-" + str(len(self.chapters)) + "]"


class Chapter(object):
    def __init__(self, title, num=-1, content=()):
        self.title = title
        self.num = num
        self.content = content
        self.id = -1
        self.path = None
        self.create_time = None
        self.update_time = None
        self.state = 0
        self.note_id = -1

    def __str__(self):
        return str(self.num) + "." + self.title + "-"

    def to_string(self):
        return self.__str__()

    def inject(self, result_dic):
        if result_dic is None:
            return

        self.content = result_dic['content']
        self.path = result_dic['path']
        self.create_time = result_dic['create_time']
        self.update_time = result_dic['update_time']
        self.state = result_dic['state']
        self.note_id = result_dic['note_id']
        self.num = result_dic['num']
        self.title = result_dic['title']
        self.id = result_dic['id']


class UrlChapter(Chapter):
    def __init__(self, url, title, num=-1, content=None):
        super().__init__(title, num, content)
        self.url = url
