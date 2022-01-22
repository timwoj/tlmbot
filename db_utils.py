import os
import sqlite3
import sys
import unittest

from furl import furl
from urllib.parse import urlparse,parse_qs
from datetime import datetime

def connect(path, read_only):

    full_path = path
    if read_only:
        full_path = f'file:{path}?mode=ro'

    conn = None
    try:
        conn = sqlite3.connect(full_path)
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

    # for Amazon URLs, there's a few things that are always true. First,
    # all params are useless and can be removed. Also, the ending part of
    # the path starting with 'ref=' can be removed, if it exists.
    if f.host.find('amazon') != -1:
        f.args.clear()
        if f.path.segments[-1].startswith('ref='):
            f.path.segments.pop()

    else:
        for k in f.args:
            if f.host.find('amazon') != -1:
                keys_to_remove.add(k)
            elif k.startswith('utm_'):
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
    ret = None

    if results:
        ret = {
            'count': results['count'],
            'paster': results['orig_paster'],
            'when': results['orig_date']
        }

        now = datetime.now().replace(microsecond = 0)

        cur.execute('update urls set count = ?, latest = ? where url = ?',
                    [results['count']+1, now, new_url])

    else:
        # insert new URL with new count and original date
        cur.execute('insert into urls (url, orig_paster) values(?, ?)',
                    [new_url, paster])

    db.commit()
    return ret

def _query_urls(db, command, stack):

    cur = db.cursor()
    if stack:
        cur.execute(command, stack)
    else:
        cur.execute(command)

    results = cur.fetchall()
    ret = []
    for r in results:
        ret.append({'url': r['url'],
                    'count': r['count'],
                    'when': r['latest']})

    return ret

def get_urls(db, day_range=None, start_date=None, end_date=None):

    command = 'select * from urls '
    stack = []

    if day_range == 'all':
        # Nothing happens here. We just have the if statement to avoid
        # fallthrough into one of the other cases
        None
    elif day_range:
        command += f'where date(latest) between date("now", "{day_range}", "localtime") and date("now","localtime")'
    elif start_date:
        command += f'where datetime(latest) between datetime(?,"unixepoch") and datetime(?,"unixepoch")'
        stack.append(start_date)
        stack.append(end_date)
    else:
        command += 'where date(latest) = date("now","localtime")'

    command += ' order by latest desc'
    return _query_urls(db, command, stack)

def search_urls(db, text):

    cur = db.cursor()
    command = 'select * from urls where url like ? order by latest desc'
    stack = [f'%{text}%']
    return _query_urls(db, command, stack)

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
        cur.execute('insert into karma (string, orig_paster) values(?, ?)',
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

    def test_filter_query(self):
        a = filter_query('https://test.com')
        self.assertEqual(a, 'https://test.com')
        a = filter_query('https://test.com?test=abcd&utm_thing=goaway')
        self.assertEqual(a, 'https://test.com?test=abcd')
        a = filter_query('https://www.amazon.com/Minions-Super-Size-Blaster-Sounds-Realistic/dp/B082G4ZZWH/ref=dp_fod_1?pd_rd_i=B082G4ZZWH&psc=1')
        self.assertEqual(a, 'https://www.amazon.com/Minions-Super-Size-Blaster-Sounds-Realistic/dp/B082G4ZZWH')

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
