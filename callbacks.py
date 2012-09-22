class ServerCallbacks(object):
    def ping(self, server, parts, line):
        """PING/PONG message
        http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_6_2
        """
        server.send('PONG %s' % parts[1][1:])
