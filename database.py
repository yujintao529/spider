import traceback

import pymysql

from note import Chapter, Note


def open_connection():
    """
    打开数据库连接，获取连接对象
    """
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='root',
                                 db='spider',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def close_connection(connection):
    """
        关闭数据库连接
    """
    connection.close()


def cursor_execute(connection, cursor_cb):
    """
    @param connection 数据库连接对象
    @param cursor_cb 闭包函数，参数是connection和cursor
    """
    with connection.cursor() as cursor:
        cursor_cb(connection, cursor)


def cursor_execute(connection):
    """
    获取数据库cursor独享
    @return 数据库cursor对象
    """
    return connection.cursor()


def insert_note_if_not_exist(connection, note):
    """
    :param connection:
    :param note:
    :return: 是否存在该小说记录
    """
    has = False
    try:
        with connection.cursor() as cursor:
            # sql = " INSERT INTO note (title) SELECT %s FROM dual WHERE not exists (select 1 from note  where title=%s ) "
            sql = "SELECT * from note where title=%s"
            cursor.execute(sql, note.title)
            result_dic = cursor.fetchone()
            if result_dic is None:
                has = False
                cursor.execute("INSERT INTO note(title) values(%s)", note.title)
                note.id = cursor.lastrowid
            else:
                has = True
                note.inject(result_dic)
    except Exception:
        traceback.print_exc()
    finally:
        connection.commit()
        return has


def insert_or_update_chapter(connection, chapter):
    """
    插入或者更新章节信息
    :param connection:
    :param chapter:
    :return: None
    """
    try:
        with connection.cursor() as cursor:

            if chapter.id != -1:
                # 已经存在了的记录需要更新
                sql = "UPDATE chapter SET state=%s,path=%s,content=%s where id=%s"
                cursor.execute(sql, (chapter.state, chapter.path, "".join(chapter.content), chapter.id))
                pass
            else:
                # 如果不存在记录直接插入
                sql = 'INSERT INTO chapter (title,state,path,content,num,note_id) values (%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql, (
                    chapter.title, chapter.state, chapter.path, ''.join(chapter.content) if chapter.content else '',
                    chapter.num, chapter.note_id))
            chapter.id = cursor.lastrowid

    except Exception:
        traceback.print_exc()
    finally:
        connection.commit()


def find_note_chapter(connection, note_id, title):
    """
    搜索章节信息的字典
    :param connection:
    :param note_id:
    :param title:
    :return: 章节信息字典
    """
    with connection.cursor() as cursor:
        sql = "select * from chapter where note_id=%s and title=%s "
        cursor.execute(sql, (note_id, title))
        return cursor.fetchone()
