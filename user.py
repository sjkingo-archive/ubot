
def test(server, req, *args):
    server.send_privmsg(req['nick'],
            'This is a test. The request was %s, the args were %s' % (req, list(args)))

def reload(server, req):
    mods = server.init_callbacks()
    server.send_privmsg(req['nick'], 'Reloaded modules %s' % mods)
    print('Reloaded modules %s as requested by %s' % (mods, req['nick']))
