import pymysql

from note import Chapter


def open_connection():
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='root',
                                 db='noteSpider',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def close_connection(connection):
    connection.close()


def cursor_execute(connection, cursor_cb):
    with connection.cursor() as cursor:
        cursor_cb(connection, cursor)


def cursor_execute(connection):
    return connection.cursor()


def insert_note_if_not_exist(connection, note):
    try:
        with connection.cursor() as cursor:
            sql = " INSERT INTO note (title) SELECT %s FROM dual WHERE not exists (select 1 from note  where title=%s ) "
            sql_note = "SELECT * from note where title=%s"
            cursor.execute(sql, (note.title, note.title))
            connection.commit()

            cursor.execute(sql_note, note.title)
            result = cursor.fetchone()
            if result is not None:
                note.id = result['id']
                note.create_time = result['create_time']
            cursor.close()

    finally:
        pass


def find_note_chapter(connection, note_id, title):
    with connection.cursor() as cursor:
        sql = "select * from chapter where note_id=%s and title=%s "
        cursor.execute(sql, (note_id, title))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            return None
        else:
            chapter=Chapter()
            chapter.inject(result)
            return chapter
