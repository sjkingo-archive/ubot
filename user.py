from util import restricted

def test(server, req, *args):
    server.send_privmsg(req['nick'],
            'This is a test. The request was %s, the args were %s' % (req, list(args)))

@restricted
def reload(server, req):
    mods = server.init_callbacks()
    server.send_privmsg(req['nick'], 'Reloaded the following modules:')
    for m in mods:
        server.send_privmsg(req['nick'], '   %s' % m)

@restricted
def authlist(server, req):
    server.send_privmsg(req['nick'], 'Authorized users of this bot are:')
    for i in server.irc_config['authorized_users']:
        if i == req['usermask']:
            suffix = ' (you)'
        else:
            suffix = ''
        server.send_privmsg(req['nick'], '   %s%s' % (i, suffix))
