import datetime
import re
from clint.textui import colored

from util import *

# --- Numeric callbacks go here ---

def numeric_001(server, parts, line):
    """Server connecting info"""
    pass
numeric_002 = numeric_001
numeric_003 = numeric_001
numeric_004 = numeric_001

def numeric_005(server, parts, line):
    """Server supports"""
    supports = line.split(' :are')[0].split(' ')[3:]
    server.server_supports.append(supports)
    pprint('This server supports: %s' % supports)

def numeric_375(server, parts, line):
    """MOTD - ignore"""
    pass
numeric_372 = numeric_375

def numeric_376(server, parts, line):
    """End of MOTD - signifies connection startup is complete"""

    pprint('Connection startup is complete')

    for i in server.irc_config['channels_to_join']:
        pprint('Joining channel %s' % i)
        server.join_channel(i, None)

_nick_num_patt = re.compile(r'([-_a-zA-Z]+)([0-9]+)')
def numeric_433(server, parts, line):
    """ERR_NICKNAMEINUSE - automatically try to change to a valid nick
    http://www.irchelp.org/irchelp/rfc/chapter6.html#c6_1
    """
    server.failed_nickchanges += 1
    if server.failed_nickchanges > 4:
        # stop repeated loops
        pprint('Too many failed NICK changes, quitting')
        server.quit(graceful=False)

    current = server.irc_config['nick']
    m = _nick_num_patt.match(current)
    if not m:
        new_nick = '%s1' % current
    else:
        prefix = m.groups()[0]
        suffix = int(m.groups()[1]) + 1
        new_nick = '%s%d' % (prefix, suffix)
    pprint('Server reports nick %s is in use, trying %s' % (current, new_nick))
    server.change_nick(new_nick)


# --- Misc callbacks go here ---

def ping(server, parts, line):
    """PING/PONG message
    http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_6_2
    """
    server.send('PONG %s' % parts[1][1:])

def mode(server, parts, line):
    if parts[2] == server.irc_config['nick']:
        # bot has had its mode changed
        old_modes = set(server.user_modes) # need to copy this
        update_modes(server.user_modes, parts[3][1:])
        pprint('Updating user modes: %s -> %s' % (old_modes, server.user_modes))
    elif parts[2] in server.joined_channels and server.irc_config['nick'] in parts[3:]:
        # bot has been given a mode on a channel
        set_by = UserMask(parts[0])
        pprint('Channel mode set for us by %s' % set_by)
    elif parts[2] in server.joined_channels and server.irc_config['nick'] not in parts[3:]:
        # channel mode has been set
        set_by = ServerMask(parts[0])
        channel = parts[2]
        mode = parts[3]
        pprint('Channel %s mode has been changed to %s by %s' % (channel, mode, set_by))
    else:
        pprint('Unknown modeline %s, ignoring' % ' '.join(parts[1:]))

def notice(server, parts, line):
    l = line.split(':***')
    pprint('Server notice: %s' % l[1])

def privmsg(server, parts, line):
    msg_from = UserMask(parts[0])
    location = parts[2]
    if location[0] in ['&', '#']:
       # channel message
       suffix = '/%s' % location
    else:
        suffix = ''
    msg = ' '.join(parts[3:])[1:]
    pprint(colored.yellow('<%s@%s>%s %s' % (msg_from.nick, msg_from.hostname, suffix, msg)))
    if msg[0] == server.irc_config['command_prefix']:
        server.handle_user_cmd(msg_from.nick, msg_from.username, msg_from.hostname, msg)


# --- Channel callbacks go here ---

def join(server, parts, line):
    chan = parts[2][1:]
    if chan in server.pending_channel_joins:
        nicks = server.pending_channel_joins[chan]
        for n in nicks:
            if n is not None:
                server.send_privmsg(n, 'I have now joined %s' % chan)
        server.joined_channels.add(chan)
        del server.pending_channel_joins[chan]

def kick(server, parts, line):
    if parts[3] != server.irc_config['nick']:
        # not us, ignore
        return

    chan = parts[2]
    kicker = parts[0][1:]
    msg = ' '.join(parts[4:])[1:]
    pprint('Kicked from %s by %s (%s)' % (chan, kicker, msg))
    server.joined_channels.remove(chan)

    if server.irc_config['rejoin_on_kick']:
        pprint('rejoin_on_kick is set, rejoining %s' % chan)
        server.join_channel(chan, None)
