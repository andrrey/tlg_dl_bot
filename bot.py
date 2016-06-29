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
db_conn = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database, charset='utf8')
bot = TelegramBot(config.get('Config', 'Token'))
bot.update_bot_info().wait()
print(bot.username + ' is up and running')


def check_new_chat(id):
	try:
		cursor1 = db_conn.cursor()
		cursor2 = db_conn.cursor()
		cursor1.execute("SELECT COUNT(*) FROM chats WHERE chat_id = %s", (str(id),))
		
		count = cursor1.fetchone()[0]

		if(0 == count):
			print('will insert chat ID ' + str(id))
			cursor2.execute("INSERT INTO chats (chat_id, room) VALUES (%s, %s)", (str(id), 'start'))			
			db_conn.commit()
		if(count > 1):
			raise ValueError('Too many records for given chat_id!')
			
	except Exception as error:
		print(error)
				
	finally:
		cursor1.close()
		cursor2.close()


def parse_scene(scene, cid):
	ret = None

	try:
		cursor = db_conn.cursor()
		cursor.execute("SELECT room from chats where chat_id = %s", (cid,))
		room = cursor.fetchone()[0]
		cursor.execute("SELECT end_text, next_room_id from rooms where room_id = %s", (room,))
		arr = cursor.fetchone()
		end_text = arr[0]
		next_room_id = arr[1]
		print('End text: ' + end_text)
		print('Next rooms is ' + next_room_id)
		if(end_text == scene):
			cursor.execute("SELECT room_text from rooms where room_id = %s", (next_room_id,))
			ret = cursor.fetchone()[0]
			print('Will return: ' + ret)
			cursor.execute("UPDATE chats set room = %s where chat_id = %s", (next_room_id, cid))
			db_conn.commit()

	except Exception as error:
		print(error)

	finally:
		cursor.close()

	return ret


def parse_command(command):
	if('/help' == command):
		return 'Команд нету пока'


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
			    		command_text = parse_command(txt)
			    		if(command_text is not None):
			    			bot.send_message(msg.chat.id, command_text)
			    			continue
			    		else:
			    			scene_text = parse_scene(txt, msg.chat.id)
			    			if(scene_text is not None):
			    				bot.send_message(msg.chat.id, scene_text)
		sleep(sleep_time)

except:
	raise

finally:
	db_conn.close()
