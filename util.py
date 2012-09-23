
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

def explode_from(f):
    """Explodes a from field in the form of ':nick!~user@host' into a tuple
    of the form (nick, user, host)"""
    parts = f.split('!')
    nick = parts[0][1:]
    user = parts[1].split('@')[0]
    if user[0] == '~':
        user = user[1:]
    host = parts[1].split('@')[1]
    return (nick, user, host)

def restricted(func):
    def _check_authorized(server, req, *args):
        if req['usermask'] in server.irc_config['authorized_users']:
            func(server, req, *args)
        else:
            server.send_privmsg(req['nick'], 'Access denied: you are not on the authorized users list.')
    return _check_authorized
