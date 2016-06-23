#!/usr/bin/python3.4

from twx.botapi import TelegramBot
import configparser
config = configparser.ConfigParser()
config.read("config.cfg")

bot = TelegramBot(config.get('Config', 'Token'))
bot.update_bot_info().wait()
print(bot.username)

while True:
	updates = bot.get_updates().wait()
	for update in updates:
	    print(update)
