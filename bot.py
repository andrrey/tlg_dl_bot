#!/usr/bin/python3.4

from twx.botapi import TelegramBot
from time import sleep
import configparser
import MySQLdb
from datetime import datetime, timedelta

sleep_time = 1

config = configparser.ConfigParser()
config.read("config.cfg")
db_host = config.get('DB', 'host')
db_user = config.get('DB', 'user')
db_pass = config.get('DB', 'password')
db_database = 'tlg_bot'
db_charset = 'utf8'
botmaster = config.get('Config', 'botmaster')
db_conn = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database, charset=db_charset)
sleepers = {}  # here we will store active timers for rooms
bot = TelegramBot(config.get('Config', 'Token'))
bot.update_bot_info().wait()
print(bot.username + ' is up and running')


def check_new_chat(cid):
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM chats WHERE chat_id = %s", (str(cid),))

        count = cursor.fetchone()[0]

        if 0 == count:
            print('will insert chat ID ' + str(cid))
            cursor.execute("INSERT INTO chats (chat_id, room) VALUES (%s, %s)", (str(cid), 'start'))
            db_conn.commit()
        if count > 1:
            raise ValueError('Too many records for given chat_id!')

    except Exception as error:
        print(error)

    finally:
        cursor.close()


def parse_scene(scene, cid):
    global sleepers
    cursor = db_conn.cursor()

    try:
        room = get_current_room(cid)
        cursor.execute("SELECT end_text, next_room_id, end_type from rooms where room_id = %s", (room,))
        end_text, next_room_id, end_type = cursor.fetchone()
        print("Room type is", end_type)
        if 0 == end_type and scene is not None:  # end with keyword
            print('End text: ' + end_text)
            print('Next room is ' + next_room_id)
            if end_text.upper() in scene.upper():
                move_to_room(next_room_id, cid)
        if 1 == end_type:  # end by time
            print("This is room with timing")
            if datetime.now() >= sleepers[cid]:  # it's time to move on
                move_to_room(next_room_id, cid)

    except Exception as error:
        print(error)

    finally:
        cursor.close()


def get_current_room(cid):
    cursor = db_conn.cursor()
    cursor.execute("SELECT room from chats where chat_id = %s", (cid,))
    room = cursor.fetchone()[0]
    cursor.close()
    return room


def move_to_room(next_room_id, cid):
    global sleepers
    cursor = db_conn.cursor()
    cursor.execute("SELECT room_text, end_type, end_delay, room_type from rooms where room_id = %s", (next_room_id,))
    text, end_type, end_delay, room_type = cursor.fetchone()
    cursor.execute("UPDATE chats set room = %s where chat_id = %s", (next_room_id, cid))

    # types of ending
    if 1 == end_type:
        sleepers[cid] = datetime.now() + timedelta(seconds=end_delay)
    else:
        sleepers[cid] = None

    # types of return
    if 0 == room_type:
        print('Will return: ' + text)
        bot.send_message(cid, text)
    elif 1 == room_type:
        print('Must return picture, but it not implemented yet')
    db_conn.commit()
    cursor.close()


def parse_command(command):
    if '/help' == command:
        return 'Команд нету пока'


def db_connection():  # Detect broken DB connection and try to reconnect
    global db_conn
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chats")
        res = cursor.fetchone()[0]
    except Exception as e:
        print("Connection to DB seems to be broken. Reason:")
        print(e)
        print("Restoring connection...")
        db_conn = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database, charset=db_charset)


offset = None

while True:
    try:
        if sleepers is not None:  # ********** STAGE ONE - check current timers
            db_connection()
            tm_now = datetime.now()
            print("Now " + tm_now.strftime("%A, %d. %B %Y %I:%M:%S%p"))
            for sleeping_chat in sleepers:
                tm = sleepers[sleeping_chat]
                if tm is not None:
                    print("Chat " + str(sleeping_chat) + " " + tm.strftime("%A, %d. %B %Y %I:%M:%S%p"))
                    if tm_now >= tm:
                        print("It's time to move out of room for chat " + str(sleeping_chat))
                        parse_scene(None, sleeping_chat)
        updates = bot.get_updates(offset).wait()
        if updates is None:  # ********** STAGE TWO - check new updates
            continue
        db_connection()
        for update in updates:
            print(update)
            offset = update.update_id + 1
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
                    if username == botmaster:
                        command_text = parse_command(txt)
                        if command_text is not None:
                            bot.send_message(msg.chat.id, command_text)
                            continue
                    parse_scene(txt, msg.chat.id)
    except Exception as e:
        print(e)

    sleep(sleep_time)

db_conn.close()

