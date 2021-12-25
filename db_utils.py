import os
import sqlite3
import sys
import unittest

from furl import furl
from urllib.parse import urlparse,parse_qs
from datetime import datetime

def connect(path):

    conn = None
    try:
        conn = sqlite3.connect(path)
    except:
        if 'unittest' not in sys.modules.keys():
            print(f'Failed to load database file \'{path}\': {sys.exc_info()[1]}')
        return None

    # Ensure we get Row objects back for queries. This makes handling
    # the results a little easier later.
    conn.row_factory = sqlite3.Row

    # Create a cursor and add the table if it doesn't exist already.
    cur = conn.cursor()
    cur.execute('create table if not exists urls('
                'url text primary key not null, '
                'count integer default 1, '
                'latest datetime not null default current_timestamp, '
                'orig_paster text not null, '
                'orig_date datetime not null default current_timestamp)')
    cur.execute('create table if not exists karma('
                'string text primary key not null, '
                'count integer default 1, '
                'orig_paster text not null, '
                'orig_date datetime not null default current_timestamp)')
    conn.commit()
    return conn

# Parses a URL and strips unwanted params from
def filter_query(url):

    f = furl(url)
    keys_to_remove = set()

    for k in f.args:
        if k.startswith('utm_'):
            keys_to_remove.add(k)

    for k in keys_to_remove:
        f.args.pop(k)

    return f.url

def store_url(db, url, paster):

    # trim all of the tracking stuff off it
    new_url = filter_query(url)

    # check if the new URI is in the database yet
    cur = db.cursor()
    cur.execute('select * from urls where url = ?', [new_url])
    results = cur.fetchone()

    if results:
        ret = {
            'count': results['count'],
            'paster': results['orig_paster'],
            'when': results['orig_date']
        }

        cur.execute('update urls set count = ?, latest = ? where url = ?',
                    [results['count']+1, datetime.now(), new_url])
        db.commit()

        return ret

    else:
        # insert new URL with new count and original date
        cur.execute('insert into urls (url, orig_paster) values(?, ?)',
                    [new_url, paster])
        db.commit()

        return None

def get_urls(db, start_date=None, end_date=None, pattern=None):

    cur = db.cursor()
    command = 'select * from urls'
    stack = []

    if start_date:
        command += ' where latest >= ?'
        stack.append(start_date)

    if end_date:
        if command.find('where') == -1:
            command += ' where'
        command += ' latest <= ?'
        stack.append(end_date)

    if pattern:
        if command.find('where') == -1:
            command += ' where'
        command += ' url like ?'
        stack.append(f'%{pattern}%')

    command += ' order by latest desc'

    cur.execute(command, stack)
    results = cur.fetchall()
    ret = []
    for r in results:
        ret.append({'url': results['url'],
                    'count': results['count'],
                    'when': results['latest']})

    return ret

def set_karma(db, text, paster, increase):
    cur = db.cursor()
    cur.execute('select * from karma where string = ?', [text])
    results = cur.fetchone()

    if results:
        count = int(results['count'])
        if increase:
            count += 1
        else:
            count -= 1
        cur.execute('update karma set count = ? where string = ?',
                    [count, text])
    else:
        cur.execute('insert into karma (string, orig_paster) values(?, ?14)',
                    [text, paster])

    db.commit()

def get_karma(db, text):
    cur = db.cursor()
    cur.execute('select * from karma where string = ?', [text])
    results = cur.fetchone()

    count = 0
    if results:
        count = int(results['count'])

    return count

class _TestCases(unittest.TestCase):

    def test_connect_failure(self):
        db = connect('/tmp/dbutil-test/sqlite.db')
        self.assertEqual(db, None)

    def test_connect_success(self):
        import tempfile
        path = os.path.join(tempfile.gettempdir(), 'testing-dbutils-sqlite.db')
        db = connect(str(path))
        self.assertNotEqual(db, None)
        db.close()
        os.unlink(str(path))

    # TODO: decide how best to test the rest of these
    def test_store_url(self):
        import tempfile
        path = os.path.join(tempfile.gettempdir(), 'testing-dbutils-sqlite.db')
        db = connect(str(path))

        db.close()
        os.unlink(str(path))

        return

    def test_get_urls(self):
        import tempfile
        path = os.path.join(tempfile.gettempdir(), 'testing-dbutils-sqlite.db')
        db = connect(str(path))

        db.close()
        os.unlink(str(path))
        return

    def test_set_karma(self):
        import tempfile
        path = os.path.join(tempfile.gettempdir(), 'testing-dbutils-sqlite.db')
        db = connect(str(path))

        db.close()
        os.unlink(str(path))
        return

    def test_get_karma(self):
        import tempfile
        path = os.path.join(tempfile.gettempdir(), 'testing-dbutils-sqlite.db')
        db = connect(str(path))

        db.close()
        os.unlink(str(path))
        return

if __name__ == "__main__":
    unittest.main()
