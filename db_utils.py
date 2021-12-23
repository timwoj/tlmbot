import sqlite3
from furl import furl
from urllib.parse import urlparse,parse_qs
from datetime import datetime

def connect(path):
    conn = sqlite3.connect(path)
    if not conn:
        print('Failed to load database file \'{:s}\''.format(config_file['database_file']))
        return None
        
    cur = conn.cursor()
    cur.execute('create table if not exists urls('
                'url text primary key not null,'
                'count integer default 1,'
                'latest datetime not null default current_timestamp,'
                'orig_paster text not null,'
                'orig_date datetime not null default current_timestamp)')
    conn.commit()
    return conn

def filter_query(f):
    keys_to_remove = set()

    for k in f.args:
        if k.startswith('utm_'):
            keys_to_remove.add(k)

    for k in keys_to_remove:
        f.args.pop(k)

    return f.url

def store_url(db, url, paster):
    # parse the URL into a URI object and trim the tracking
    # stuff off it
    parsed = furl(url)

    # trim all of the tracking stuff off it
    new_url = filter_query(parsed)

    # check if the new URI is in the database yet
    cur = conn.cursor()
    cur.execute('select * from links where url = ?', new_url)
    results = cur.fetchone()

    if results:
        ret = {
            'count': results['count'],
            'paster': results['orig_paster'],
            'when': results['orig_date']
        }

        cur.execute('update links (count, latest) set (?,?) where url = ?',
                    results['count']+1, datetime.now(), new_url)

        return ret

    else:
        # insert new URL with new count and original date
        cur.execute('insert into links(url, paster) values(?, ?)',
                    new_url, paster)

        return None

def get_urls(db, start_date, end_date, pattern):
    print('get_urls')
