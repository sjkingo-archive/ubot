from __future__ import print_function
import re
import socket

import callbacks

VERSION = '0.1'

class IRCBot(object):
    sock = None
    fp = None

    server_callbacks = None

    user_modes = set()

    def __init__(self, server='localhost', port=6667, nick='ubot'):
        self.irc_config = {
                'server': server,
                'port': port,
                'nick': nick,
                'user': nick,
                'name': 'ubot',
        }
        self.init_callbacks()
        print('ubot v%s starting up' % VERSION)

    def init_callbacks(self):
        if self.server_callbacks is not None:
            del self.server_callbacks
            reload(callbacks)
        self.server_callbacks = callbacks.ServerCallbacks()

    def send(self, line):
        print(' >> %s' % line)
        print(line, end='\r\n', file=self.fp)

    def readline(self):
        l = self.fp.readline().strip()
        print(' << %s' % l)
        return l

    def connect(self):
        self.sock = socket.create_connection(
                (self.irc_config['server'], self.irc_config['port']))
        self.fp = self.sock.makefile('rw', 0)
        print('Connected to %s:%d' % (self.irc_config['server'], self.irc_config['port']))
        self.send('NICK %s' % self.irc_config['nick'])
        self.send('USER %s 8 * :%s' % (self.irc_config['user'], self.irc_config['name']))

    def dispatch(self):
        while True:
            try:
                l = self.readline()
            except socket.timeout:
                print('Socket timeout (server not responding), quitting')
                self.quit(graceful=False) # don't send quit message
            except KeyboardInterrupt:
                self.quit(msg='I was sent SIGINT')
            else:
                self._handle_line(l)

    def quit(self, graceful=True, msg='Goodbye'):
        if graceful:
            self.send('QUIT :%s' % msg)
            print('Quitting (%s)' % msg)
        exit(0)

    _startup_prefix_patt = re.compile(r'[0-9]{3}')
    def _handle_line(self, line):
        if len(line) == 0:
            print('Server closed connection, quitting')
            self.quit(graceful=False) # don't send quit message

        parts = line.split(' ')
        if parts[0][0] == ':':
            key = parts[1]
        else:
            key = parts[0]
        
        # special case for startup messages
        if self._startup_prefix_patt.match(key):
            # do nothing
            return

        # otherwise, dispatch this to a callback
        callback = getattr(self.server_callbacks, key.lower(), None)
        if callback is not None:
            callback(self, parts, line)
        else:
            print('Unhandled server command %s' % key)
