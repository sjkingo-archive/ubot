#!/usr/bin/python

import ubot

def main():
    bot = ubot.IRCBot()
    bot.connect()
    bot.dispatch()


if __name__ == '__main__':
    main()
