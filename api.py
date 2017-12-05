import json
import sqlite3
import calendar
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

with open('config.json', 'rb') as fh:
    app.config.update( **json.load( fh ) )

if 'debug' in app.config.keys():
    app.debug = app.config['debug']
else:
    app.debug = False

def create_db_instance():
    return sqlite3.connect( app.config['dbfile'] )

@app.route('/')
def get_messages():
    filters_available = []
    filters_available.append({
        'filter':           'recipients LIKE "%" || ? || "%"',
        'request_param':    'to'
    })
    filters_available.append({
        'filter':           'sender LIKE "%" || ? || "%"',
        'request_param':    'from'
    })
    filters_available.append({
        'filter':           'subject LIKE "%" || ? || "%"',
        'request_param':    'subject'
    })
    filters_available.append({
        'filter':           'body LIKE "%" || ? || "%"',
        'request_param':    'body'
    })
    filters_available.append({
        'filter':           'timestamp < ?',
        'request_param':    'before',
        'param_coerce':     'datetime',
        'binding_coerce':   'timestamp',
        'param_coerce_options': {
            'format_in':    '%Y-%m-%dT%H:%M:%S',
        }
    })

    filters = []
    parameters = []

    for f in filters_available:
        param = request.values.get(f['request_param'], False)
        if param:
            if 'param_coerce' in f.keys():
                if f['param_coerce'] == 'datetime':
                    param = datetime.strptime( param, f['param_coerce_options']['format_in'] )

            if 'binding_coerce' in f.keys():
                if f['binding_coerce'] == 'timestamp':
                    param = calendar.timegm( param.timetuple() )

            filters.append( f['filter'] )
            parameters.append( str(param) )

    query = 'SELECT * FROM messages WHERE %s' % ' AND '.join(filters)
    app.logger.debug('Query: %s' % query)
    app.logger.debug('Parameters (%s): %s' % (len(parameters), ', '.join(parameters)))

    db = create_db_instance()
    c = db.cursor()
    c.execute(query, parameters)
    rows = [row for row in c]
    db.close()

    app.logger.debug('Retrieved %d rows from database' % len(rows))

    messages = []
    for row in rows:
        message = {}
        message['timestamp'] = datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S')
        message['from'] = row[2]
        message['recipients'] = row[3].split(',')
        message['subject'] = row[4]
        message['body'] = row[5]
        message['headers'] = json.loads( row[6] ) if row[6] is not None else []
        messages.append(message)

    response = {}
    response['count'] = len(messages)
    response['messages'] = messages

    return jsonify(response)

if __name__ == '__main__':
    app.run()
