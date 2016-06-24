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
	    #print(update)
	    offset=update.update_id + 1
	    msg = update.message
	    if msg is not None:
	    	fromuser = msg.from
	    	txt = msg.text.decode("utf-8")
	    	username = fromuser.first_name.decode("utf-8")
	    	if fromuser.last_name is not None:
	    		username += fromuser.last_name.decode("utf-8")
	    	print('From: ' + username + ': ' + txt)	    	

	sleep(sleep_time)
