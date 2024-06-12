#!/usr/bin/python
# coding=utf-8

import sys
import time
import sqlite3
import telepot
from pprint import pprint
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
import traceback

import noti


def replyPrkData(date_param , user, loc_param='260-2-000068'):
    print(user, loc_param)
    res_list = noti.getData( loc_param)
    print(res_list)
    msg = ''
    for r in res_list:
        print( str(datetime.now()).split('\n')[0], r )
        if len(r+msg)+1 > noti.MAX_MSG_LENGTH:
            noti.sendMessage( user, msg )
            msg = r+ '\n'
        else:
            msg += r+'\n'

    if msg:
        noti.sendMessage( user, msg )
    else:
        noti.sendMessage( user, '해당하는 데이터가 없습니다.' )

def check( user ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    cursor.execute('SELECT * from users WHERE user="%s"' % user)
    for data in cursor.fetchall():
        row = 'id:' + str(data[0]) + ', location:' + data[1]
        noti.sendMessage( user, row )


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        noti.sendMessage(chat_id, '난 텍스트 이외의 메시지는 처리하지 못해요.')
        return

    text = msg['text']
    args = text.split(' ')

    if text.startswith('주차장') and len(args) > 1:
        print('try to 주차장', args[1])
        replyPrkData('주차장', chat_id, args[1] )
    elif text.startswith('확인'):
        print('try to 확인')
        check( chat_id )
    else:
        noti.sendMessage(chat_id, """모르는 명령어입니다. 주차장 번호를 입력해주세요 ex) 주차장 260-2-000068 """)


def telegram_main():

    today = date.today()
    current_month = today.strftime('%Y%m')

    print( '[',today,']received token :', noti.TOKEN )

    bot = telepot.Bot(noti.TOKEN)
    pprint( bot.getMe() )

    bot.message_loop(handle)

    print('Listening...')
