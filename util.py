
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

class UserMask(object):
    def __init__(self, mask):
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
