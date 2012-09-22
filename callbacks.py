import re

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

    _nick_num_patt = re.compile(r'([-_a-zA-Z]+)([0-9]+)')
    def numeric_433(self, server, parts, line):
        """ERR_NICKNAMEINUSE - automatically try to change to a valid nick
        http://www.irchelp.org/irchelp/rfc/chapter6.html#c6_1
        """
        server.failed_nickchanges += 1
        if server.failed_nickchanges > 4:
            # stop repeated loops
            print('Too many failed NICK changes, quitting')
            server.quit(graceful=False)

        current = server.irc_config['nick']
        m = self._nick_num_patt.match(current)
        if not m:
            new_nick = '%s1' % current
        else:
            prefix = m.groups()[0]
            suffix = int(m.groups()[1]) + 1
            new_nick = '%s%d' % (prefix, suffix)
        print('Server reports nick %s is in use, trying %s' % (current, new_nick))
        server.change_nick(new_nick)
