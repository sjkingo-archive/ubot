#!/usr/bin/python

import ubot

def main():
    authorized_users=set([
        'sam!sam@127.0.0.1',
    ])
    channels_to_join=set([
        '#a',
    ])
    bot = ubot.IRCBot(
            authorized_users=authorized_users,
            channels_to_join=channels_to_join
    )
    bot.connect()
    bot.dispatch()


if __name__ == '__main__':
    main()
