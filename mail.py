import os
import smtpd
import asyncore
import json
import sqlite3
import time
from email import message_from_string

class MailProcessor(smtpd.SMTPServer, object):

    def __init__(self, config, db):
        self.db = db
        localaddr = (config.serverhost, config.serverport)
        super(MailProcessor, self).__init__(localaddr, None)
        print 'Server initialized'

    def process_message(self, peer, sender, recipients, data):
        print 'Message received from server %s:%s' % peer

        msg = message_from_string( data )

        content = None
        contenttype = None
        headers = []

        for part in msg.walk():
            contenttype = part.get_content_type()
            if part.get_content_type() in ['text/html', 'text/plain']:
                content = part.get_payload(decode=True)
            if part.get_content_type() == 'text/html':
                break


        c = self.db.cursor()
        c.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
            int( time.time() ),
            peer[0],
            sender,
            ','.join(recipients),
            msg['Subject'],
            content,
            json.dumps( dict( msg.items() ) ),
            contenttype
        ))
        self.db.commit()
        print 'Added message to database'

class Config(object):
    def __init__(self, defaults={}):
        self.update_from_dict( defaults )
    def update_from_json(self, filename):
        with open(filename, 'rb') as fh:
            self.update_from_dict( json.load(fh) )
    def update_from_dict(self, configs):
        for k, v in configs.iteritems():
            setattr(self, k, v)
    def __setattr__(self, key, value):
        key = key.upper()
        super(Config, self).__setattr__(key, value)
    def __getattr__(self, key):
        key = key.upper()
        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise KeyError('Missing config variable: %s' % key)

def initdb(db):
    c = db.cursor()

    c.execute('''
        CREATE TABLE messages (
            timestamp,
            peerip,
            sender,
            recipients,
            subject,
            body,
            headers,
            contenttype
        )''')

    db.commit()
    print 'Database initialized successfully'

def runserver():
    print 'HELLO! This is the Mail Processor!'

    config = Config({
        'serverhost':           'localhost',
        'serverport':           25
    })
    config.update_from_json( 'config.json' )

    if not os.path.isfile( config.dbfile ):
        need_db_init = True
        print 'Database file does not exist: %s' % config.dbfile
    else:
        need_db_init = False

    db = sqlite3.connect( config.dbfile )

    if need_db_init:
        initdb( db )

    server = MailProcessor(config, db)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print 'Shutdown received'
    finally:
        db.close()

if __name__ == '__main__':
    runserver()
