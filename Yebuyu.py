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
from util import debug
from util import convert_num

__baseUrl__ = 'https://www.88dus.com/xiaoshuo/49/49506/'


class YebuyuEngine(Engine):

    def __init__(self):
        super().__init__()
        self.note = Note("夜不语诡异档案")

    def execute(self):
        debug("开始抓取夜不语小说...")
        load_engine = LoadEngine(__baseUrl__)
        chapters = YebuyuMuLuResolve(load_engine.execute()).execute()
        self.note.chapters = chapters
        reqs = threadpool.makeRequests(YebuyuEngine.__resolve_chapter, chapters)
        [g_pool.putRequest(req) for req in reqs]
        g_pool.wait()
        debug("结束抓取夜不语小说")
        return self.note

    @staticmethod
    def __resolve_chapter(url_chapter):
        try:
            load_engine = LoadEngine(url_chapter.url)
            chapter_content = YebuyuChapterResolve(load_engine.execute()).execute()
            debug("抓取小说章节 " + url_chapter.url + " success")
            url_chapter.content = chapter_content
            file = note.chapter_disk_handler(url_chapter, "夜不语诡异档案", url_chapter.title)
            url_chapter.file = file
            debug("save to disk :" + url_chapter.file)
        except Exception:
            debug("夜不语resolve_chapter error")
            traceback.print_exc()


class YebuyuMuLuResolve(ResolveEngine):

    def __init__(self, content):
        super().__init__(content)

    def execute(self):
        chapters = list()
        mulu = self.soup.select(".mulu > ul li a")
        for index, child in enumerate(mulu):
            title = child.string.strip().replace(" ", "")
            title = convert_num(title)
            title.replace("^.//.", "")
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
