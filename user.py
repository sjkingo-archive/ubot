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

@restricted
def quit(server, req, *msg):
    server.send_privmsg(req['nick'], 'Quitting on your request. Goodbye.')
    l = list(msg)
    if len(l) == 0:
        server.quit()
    else:
        server.quit(msg=' '.join(l))

@restricted
def join(server, req, chan):
    if chan[0] not in ['#', '&']:
        server.send_privmsg(req['nick'], 'Please specify channel name correctly (missing #/& prefix)')
        return
    if chan in server.joined_channels:
        server.send_privmsg(req['nick'], 'I am already joined to %s' % chan)
        return
    if chan in server.pending_channel_joins:
        server.send_privmsg(req['nick'], 'I am already trying to join %s' % chan)
        return
    print('Joining channel %s at the request of %s' % (chan, req['nick']))
    server.join_channel(chan, req['nick'])
