from __future__ import print_function
from clint.textui import puts, colored, indent
import re
import socket

import callbacks as server_callbacks
import user as user_callbacks

VERSION = '0.1'

class IRCBot(object):
    sock = None
    fp = None

    user_modes = set()
    failed_nickchanges = 0
    server_supports = []

    joined_channels = set()
    pending_channel_joins = {}

    def __init__(self, server='localhost', port=6667, nick='ubot', command_prefix='!',
            authorized_users=set()):
        self.irc_config = {
                'server': server,
                'port': port,
                'nick': nick,
                'user': nick,
                'name': 'ubot v%s' % VERSION,
                'command_prefix': command_prefix,
                'authorized_users': authorized_users,
        }
        self.init_callbacks()

        print('ubot v%s starting up' % VERSION)

        print('Authorized users of this bot are (send bot !authlist for on-network list):')
        for i in self.irc_config['authorized_users']:
            with indent(4):
                puts(i)

        print('Legend for colour coded text:')
        with indent(4):
            puts(colored.cyan('Messages sent to server (cyan)'))
            puts(colored.red('Unimplemented responses (red)'))
            puts(colored.yellow('Private messages (yellow)'))
            puts(colored.blue('Server messages (blue)'))
        puts()

    def init_callbacks(self):
        mods = [server_callbacks, user_callbacks]
        for i in mods:
            reload(i)
        return mods

    def send(self, line):
        puts(colored.cyan('>> %s' % line))
        print(line, end='\r\n', file=self.fp)

    def readline(self):
        l = self.fp.readline().strip()
        return l

    def connect(self):
        self.sock = socket.create_connection(
                (self.irc_config['server'], self.irc_config['port']))
        self.fp = self.sock.makefile('rw', 0)
        print('Connected to %s:%d, registering as %s!%s (%s)' % 
                (self.irc_config['server'], self.irc_config['port'], 
                self.irc_config['nick'], self.irc_config['user'], self.irc_config['name']))
        self.change_nick(self.irc_config['nick'])
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

    def change_nick(self, new_nick):
        self.irc_config['nick'] = new_nick
        self.send('NICK %s' % new_nick)

    def quit(self, graceful=True, msg='Goodbye'):
        if graceful:
            self.send('QUIT :%s' % msg)
            print('Quitting (%s)' % msg)
        exit(0)

    _numeric_msg_patt = re.compile(r'[0-9]{3}')
    def _handle_line(self, line):
        if len(line) == 0:
            print('Server closed connection, quitting')
            self.quit(graceful=False) # don't send quit message

        parts = line.split(' ')
        if parts[0][0] == ':':
            key = parts[1]
        else:
            key = parts[0]
        
        # special case for numeric messages
        if self._numeric_msg_patt.match(key):
            key = 'numeric_%s' % key

        callback = getattr(server_callbacks, key.lower(), None)
        if callback is not None:
            callback(self, parts, line)
        else:
            puts(colored.red('Unhandled %s << %s' % (key, line)))

    def handle_user_cmd(self, nick, user, host, msg):
        msg_parts = msg[1:].split(' ')
        cmd = msg_parts[0].lower()
        args = msg_parts[1:]
        callback = getattr(user_callbacks, cmd, None)
        if callback is not None:
            req = { 'nick': nick,
                    'usermask': '%s!%s@%s' % (nick, user, host),
                    'msg': msg }
            try:
                callback(self, req, *args)
            except TypeError, e:
                if str(e).startswith('%s() takes exactly' % cmd):
                    m = '%s%s %s' % (self.irc_config['command_prefix'], cmd, 
                            ' '.join(str(e).split(' ')[1:]))
                    self.send_privmsg(nick, m)
                else:
                    # something else other than invalid args
                    raise
        else:
            self.send_privmsg(nick, '%s%s is not a valid command' % (self.irc_config['command_prefix'], cmd))

    def send_privmsg(self, nick, msg):
        self.send(':%s PRIVMSG %s :%s' % (self.irc_config['nick'], nick, msg))

    def join_channel(self, chan, requester):
        self.send('JOIN %s' % chan)
        if chan not in self.pending_channel_joins:
            self.pending_channel_joins[chan] = []
        self.pending_channel_joins[chan].append(requester)
        # we need to wait for a response from the server before confirming
