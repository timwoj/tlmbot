import os
import re
import sys
import json
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
app.debug = True

# Add the parent path to sys.path so we can search for modules in it
# for utility code, plus get the root path to find the config file.
script_file = Path(__file__).resolve()
root_path = script_file.parents[1]
sys.path.append(str(root_path))

import db_utils

config_file = open(root_path.joinpath('config.json'))
config = json.load(config_file)

if not config:
    print('Failed to load config file')
    sys.exit(1)

url_regex = re.compile(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)',
                       re.IGNORECASE | re.DOTALL)
def replace_url_links(s):
    return url_regex.sub(r'<a href="\1" target="_blank">\1</a>', s)

app.jinja_env.filters['replace_url_links'] = replace_url_links

@app.route('/urls', methods=['GET','POST'])
def url_page():

    db = db_utils.connect(config['database_file'])
    if not db:
        # TODO: return a 500 error here
        return ''

    # This allows sqlite3 to get past strings in columns that fail to decode as valid
    # utf-8 strings.
    db.text_factory = lambda b: b.decode(errors = 'ignore')

    start_date = None
    end_date = None
    search = None

    # create an sql query based on the current requested filter.  by default,
    # display the last week's worth of entries.  the entries are sorted with
    # teh last one first, so that displaying them is easier.
    days_shown = ''
    results = []
    if request.method == 'GET':

        results = db_utils.get_urls(db, day_range='-6 days')
        days_shown = "Showing the last 7 days"

    else:

        command = request.form.get('bsubmit',[''])
        if command == 'Filter':
            filter=request.form.get('filter',[''])
            if (filter == 'week'):
                results = db_utils.get_urls(db, day_range='-6 days')
                days_shown = "Showing the last 7 days"
            elif (filter == 'today'):
                results = db_utils.get_urls(db)
                days_shown = "Showing urls from today"
            elif (filter == 'month'):
                results = db_utils.get_urls(db, day_range='-1 month')
                days_shown = "Showing the last month"
            elif (filter == 'all'):
                results = db_utils.get_urls(db, day_range='all')
                days_shown = "Showing all of the urls stored in the database"
            elif (filter == 'date'):
                try:
                    start_field = request.form.get('start','')
                    start_date = strptime(start_field, '%Y-%m-%d').localtime()
                except ValueError:
                    # TODO: handle error here
                    print("Starting date invalid")

                try:
                    end_field = request.form.get('end','')
                    end_date = strptime(end_field, '%Y-%m-%d').localtime()
                except ValueError:
                    # TODO: handle error here
                    print("Ending date invalid")

                # set the end date to the be 1 second before the next day
                end_date = end_date + 60*60*24 - 1

                results = db_utils.get_urls(db, start_date=start_date, end_date=end_date)
                days_shown = f'Showing urls between {startdate} and {enddate}'

        elif command == 'Search':

            search = request.form.get('search', '')
            results = db_utils.search_urls(db, search)
            days_shown = f'Showing the results of query for "{search}"'

    template_values = {
        'now_str': datetime.now().strftime('%m/%d/%Y %H:%M:%S %Z'),
        'days_shown': days_shown,
    }

    response_body = render_template('url_header.html', **template_values)

    current_date = ''
    firstpass = True

    for result in results:
        dateval = result['when'].split(' ')[0]
        if current_date != dateval:
            if firstpass == False:
                response_body += '</table>\n'
            response_body += '    <p/>\n\n'
            response_body += f'    <h3><u>{dateval}</u></h3>\n'
            response_body += '    <table>\n'

            firstpass = False
            current_date = dateval

        template_values = {
            'time' : result['when'].split(' ')[1],
            'origurl' : result['url'],
            'count' : result['count']
        }

        response_body += render_template('url_entry.html', **template_values)

    response_body += '</table>\n'
    response_body += '  </body>\n'
    response_body += '</html>'
    return response_body

if __name__ == '__main__':
    app.run(host='10.0.0.9', port=8084)
