import util

class ServerCallbacks(object):
    def ping(self, server, parts, line):
        """PING/PONG message
        http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_6_2
        """
        server.send('PONG %s' % parts[1][1:])

    def mode(self, server, parts, line):
        modeline = parts[3][1:]
        if parts[2] != server.irc_config['nick']:
            print('Modeline %s was not for us, ignoring' % modeline)
            return
        old_modes = set(server.user_modes) # need to copy this
        util.update_modes(server.user_modes, modeline)
        print('Updating user modes: %s -> %s' % (old_modes, server.user_modes))
