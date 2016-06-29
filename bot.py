#!/usr/bin/python3.4

from twx.botapi import TelegramBot
from time import sleep
import configparser
import MySQLdb

sleep_time = 1

config = configparser.ConfigParser()
config.read("config.cfg")
db_host = config.get('DB', 'host')
db_user = config.get('DB', 'user')
db_pass = config.get('DB', 'password')
db_database = 'tlg_bot'
botmaster = config.get('Config', 'botmaster')
db_conn = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database)
bot = TelegramBot(config.get('Config', 'Token'))
bot.update_bot_info().wait()
print(bot.username + 'is up and running')


def check_new_chat(id):
	try:
		cursor1 = db_conn.cursor()
		cursor2 = db_conn.cursor()
		cursor1.execute("SELECT COUNT(*) FROM chats WHERE chat_id = %s", (str(id),))
		
		if(0 == cursor1.fetchone()[0]):
			print('will insert chat ID ' + str(id))
			cursor2.execute("INSERT INTO chats (chat_id, room) VALUES (%s, %s)", (str(id), 'start'))			
			db_conn.commit()
			
	except MySQLError as error:
		print(error)
				
	finally:
		cursor1.close()
		cursor2.close()


def parse_command(command):
	return False


def parse_scene(scene, id):
	return 'я тупой бот :('


offset=None

try:
	while True:
		updates = bot.get_updates(offset).wait()
		for update in updates:
		    print(update)
		    offset=update.update_id + 1
		    msg = update.message
		    if msg is not None:
		    	fromuser = msg.sender
		    	txt = msg.text
		    	check_new_chat(msg.chat.id)
		    	if txt is not None:
			    	humanname = fromuser.first_name
			    	userid = fromuser.id
			    	username = fromuser.username
			    	if fromuser.last_name is not None:
			    		humanname += ' ' + fromuser.last_name
			    	print('From ' + humanname + ' ' + txt + ' (id ' + str(userid) + '): ' + txt)
			    	if(username == botmaster):
			    		if(parse_command(txt)):
			    			continue
			    		else:
			    			bot.send_message(msg.chat.id, parse_scene(txt, userid))
		sleep(sleep_time)

except:
	raise

finally:
	db_conn.close()
