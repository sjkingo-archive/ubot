from __future__ import print_function
import socket

VERSION = '0.1'

class IRCBot(object):
    sock = None
    fp = None

    def __init__(self, server='localhost', port=6667, nick='ubot'):
        self.irc_config = {
                'server': server,
                'port': port,
                'nick': nick,
                'user': nick,
                'name': 'ubot',
        }
        print('ubot v%s starting up' % VERSION)

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
                print('Quitting')
                self.quit()
            else:
                self._handle_line(l)

    def quit(self, graceful=True):
        exit(0)

    def _handle_line(self, line):
        if len(line) == 0:
            print('Server closed connection, quitting')
            self.quit(graceful=False) # don't send quit message
        pass
