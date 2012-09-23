
def test(server, req, *args):
    server.send_privmsg(req['nick'],
            'This is a test. The request was %s, the args were %s' % (req, list(args)))

def reload(server, req):
    mods = server.init_callbacks()
    server.send_privmsg(req['nick'], 'Reloaded the following modules:')
    for m in mods:
        server.send_privmsg(req['nick'], '   %s' % m)
