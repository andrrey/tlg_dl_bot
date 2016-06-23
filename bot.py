#!/usr/bin/python3.4

from twx.botapi import TelegramBot
from time import sleep
import configparser

sleep_time = 1

config = configparser.ConfigParser()
config.read("config.cfg")
bot = TelegramBot(config.get('Config', 'Token'))
bot.update_bot_info().wait()
print(bot.username)

offset=None

while True:
	updates = bot.get_updates(offset).wait()
	for update in updates:
	    print(update)
	    offset=update.update_id + 1
	sleep(sleep_time)
