#!/usr/bin/python3.4

from twx.botapi import TelegramBot
from time import sleep
import configparser
import _mysql

sleep_time = 1

config = configparser.ConfigParser()
config.read("config.cfg")
db_host = config.get('DB', 'host')
db_user = config.get('DB', 'user')
db_pass = config.get('DB', 'password')
db_database = 'telegrambot'
botmaster = config.get('Config', 'botmaster')
db_conn = _mysql.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database)
bot = TelegramBot(config.get('Config', 'Token'))
bot.update_bot_info().wait()
print(bot.username + 'is up and running')


def parse_command(command):
	return False


def parse_scene(scene, id):
	return 'я тупой бот :('


offset=None

while True:
	updates = bot.get_updates(offset).wait()
	for update in updates:
	    #print(update)
	    offset=update.update_id + 1
	    msg = update.message
	    if msg is not None:
	    	fromuser = msg.sender
	    	txt = msg.text
	    	username = fromuser.first_name
	    	userid = fromuser.id
	    	if fromuser.last_name is not None:
	    		username += ' ' + fromuser.last_name
	    	print('From ' + username + txt + ' (id ' + userid + '): ' + txt)
	    	if(userid == botmaster):
	    		if(parse_command(txt)):
	    			continue
	    		else:
	    			bot.send_message(msg.chat.id, parse_scene(txt, userid))
	sleep(sleep_time)
