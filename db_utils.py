import sqlite3
from furl import furl
from urllib.parse import urlparse,parse_qs
from datetime import datetime

def connect(path):
    conn = sqlite3.connect(path)
    if not conn:
        print('Failed to load database file \'{:s}\''.format(config_file['database_file']))
        return None

    # Ensure we get Row objects back for queries. This makes handling
    # the results a little easier later.
    conn.row_factory = sqlite3.Row

    # Create a cursor and add the table if it doesn't exist already.
    cur = conn.cursor()
    cur.execute('create table if not exists urls('
                'url text primary key not null,'
                'count integer default 1,'
                'latest datetime not null default current_timestamp,'
                'orig_paster text not null,'
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

def get_urls(db, start_date, end_date, pattern):
    print('get_urls')
