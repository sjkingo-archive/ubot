from __future__ import print_function
from clint.textui import colored
import datetime

def update_modes(mode_set, line):
    """Parses the MODE line given and updates the mode_set - note this modifies
    the set inplace."""

    op = None
    for i in line:
        if i in ['+', '-']:
            op = i
            continue
        elif i.isalpha():
            if op is None:
                # discard, invalid modeline
                continue
            if op == '+':
                mode_set.add(i)
            else:
                mode_set.remove(i)

class ServerMask(object):
    def __init__(self, mask):
        self.hostname = mask
        if mask[0] == ':':
            self.hostname = self.hostname[1:]

    def __str__(self):
        return self.hostname

    def __repr__(self):
        return '<ServerMask %s>' % self.hostname

class UserMask(object):
    def __init__(self, mask):
        if '!' not in mask and '@' not in mask:
            # probably a server mask
            raise TypeError('Not a usermask')

        parts = mask.split('!')
        self.nick = parts[0]
        if self.nick[0] == ':':
            self.nick = self.nick[1:]
        self.username = parts[1].split('@')[0]
        if self.username[0] == '~':
            self.username = self.username[1:]
        self.hostname = parts[1].split('@')[1]

    def __str__(self):
        return '%s!%s@%s' % (self.nick, self.username, self.hostname)

    def __repr__(self):
        return '<UserMask %s>' % str(self)

def restricted(func):
    def _check_authorized(server, req, *args):
        if req['usermask'] in server.irc_config['authorized_users']:
            func(server, req, *args)
        else:
            server.send_privmsg(req['nick'], 'Access denied: you are not on the authorized users list.')
    return _check_authorized

def pprint(line, indent=0):
    now = datetime.datetime.now().strftime('%H:%M:%S')
    prefix = colored.magenta(str(now) + ':') + ' '
    print(prefix, end='')
    if indent > 0:
        print(' ' * indent, end='')
    print(line)
