#!/usr/bin/python

import ubot

def main():
    bot = ubot.IRCBot(authorized_users=set(['sam!sam@127.0.0.1']))
    bot.connect()
    bot.dispatch()


if __name__ == '__main__':
    main()
