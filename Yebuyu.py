import traceback

import threadpool
from bs4 import NavigableString

import note
from note import Engine
from note import LoadEngine
from note import Note
from note import ResolveEngine
from note import UrlChapter
from note import pool as g_pool
import log
from util import convert_num
import database

__baseUrl__ = 'https://www.88dus.com/xiaoshuo/49/49506/'

__local_debug__ = False

import multiprocessing as mp


class YebuyuEngine(Engine):

    def __init__(self):
        super().__init__()
        self.note = Note("夜不语诡异档案")
        self.connection = database.open_connection()
        self.lock = mp.Lock()

    def execute(self):
        log.debug("开始抓取夜不语小说...")
        load_engine = LoadEngine(__baseUrl__)
        chapters = YebuyuMuLuResolve(load_engine.execute()).execute()
        self.note.chapters = chapters
        has_exist = database.insert_note_if_not_exist(self.connection, self.note)
        if has_exist:
            chapters = self.find_error_and_update_chapters()

        requests = list()
        if chapters is not None and len(chapters) != 0:
            for chapter in chapters:
                requests.append(threadpool.WorkRequest(YebuyuEngine.__resolve_chapter, (self, chapter)))
            [g_pool.putRequest(req) for req in requests]
            g_pool.wait()

        log.debug("结束抓取夜不语小说" + self.note.simple_str())
        return self.note

    def find_error_and_update_chapters(self):
        """
        搜索上次抓取失败和新章节
        :return:
        """
        if self.note.chapters is None:
            return None
        found_chapters = list()
        for chapter in self.note.chapters:
            chapter.note_id = self.note.id
            result_dic = database.find_note_chapter(self.connection, chapter.note_id, chapter.title)

            if result_dic is None:
                # database.insert_or_update_chapter(self.connection, chapter)
                found_chapters.append(chapter)
                log.debug('find  update  chapter ' + chapter.to_string())
            else:
                chapter.inject(result_dic)
                if not note.is_normal(chapter.state):
                    found_chapters.append(chapter)
                    log.debug('find error  chapter ' + chapter.to_string())
                else:
                    log.debug("chapter " + chapter.to_string() + " has loaded and ignore it")

        return found_chapters

    def exit(self):
        """
        退出代码
        :return:
        """
        database.close_connection(self.connection)

    def __resolve_chapter(self, url_chapter):
        """
        抓取小说内容
        :param url_chapter:
        :return:
        """
        url_chapter.note_id = self.note.id
        load_engine = LoadEngine(url_chapter.url)
        result = load_engine.execute()
        if result is None:
            url_chapter.state = 9999
        else:
            try:
                chapter_content = YebuyuChapterResolve(result).execute()
                log.debug("loaded chapter " + url_chapter.title + "  " + url_chapter.url)
                url_chapter.content = chapter_content
                path = note.chapter_disk_handler(url_chapter, self.note.title, url_chapter.title)
                url_chapter.path = path
                log.debug("save chapter content to disk " + url_chapter.title + " - " + url_chapter.path)
                url_chapter.state = 1000
            except Exception:
                log.debug("resolve chapter " + url_chapter.title + " error")
                traceback.print_exc()
                url_chapter.state = 9999

        try:
            self.lock.acquire()
            database.insert_or_update_chapter(self.connection, url_chapter)
        finally:
            self.lock.release()


class YebuyuMuLuResolve(ResolveEngine):

    def __init__(self, content):
        super().__init__(content)

    def execute(self):
        chapters = list()
        mulu = self.soup.select(".mulu > ul li a")
        for index, child in enumerate(mulu):
            # 如果是debug，加载10个
            if __local_debug__:
                if len(chapters) >= 20:
                    break

            title = child.string.strip().replace(" ", "")
            title = convert_num(title)
            titles = title.split(".")
            if len(titles) == 2:
                if len(titles[1]) != 0:
                    title = titles[1]
            chapters.append(UrlChapter(__baseUrl__ + child.get('href'), title, index))

        return chapters


class YebuyuChapterResolve(ResolveEngine):

    def __init__(self, content):
        super().__init__(content)

    def execute(self):
        content = self.soup.select(".yd_text2")[0]
        contents = list()
        for tag in content.children:
            if isinstance(tag, NavigableString):
                str = tag.string.replace("\r\n", "").replace("\xa0", "").strip()
                if str != "":
                    contents.append("   " + str)
        return contents
