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

key = 'OhqZIlJ2117DZPpq83eQross3rg03ldy13MwmQ%2Bdut9ItVp4wCaFPedERueZLsh3kq38pKP3n6rn0DUp7ylrFA%3D%3D'
TOKEN = '7229794809:AAH_K06_579TGoCz6B54EAMV4JkUsyFM_g4'
MAX_MSG_LENGTH = 1000
baseurl = 'http://api.data.go.kr/openapi/tn_pubr_prkplce_info_api?ServiceKey=' + key
bot = telepot.Bot(TOKEN)


def getData(loc_param):
    res_list = []
    url = baseurl + '&prkplceNo=' + loc_param
    res_body = urlopen(url).read()
    soup = BeautifulSoup(res_body, 'xml')
    items = soup.findAll('item')
    for item in items:
        item = re.sub('<.*?>', '|', item.text)
        parsed = item.split('|')
        try:
            row = (parsed[0] + ', \n' + parsed[1] + ' \n' + parsed[2] + ' \n' + parsed[3] + ' \n' + parsed[4] + ', \n' +
                   parsed[5] + ', \n' + parsed[6] + ', \n' + parsed[7] + '\n')
        except IndexError:
            row = item.replace('|', ',')

    if row and row.strip() not in res_list:  # 중복 체크 후 추가
        res_list.append(row.strip())
    return res_list


def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)


def run(date_param, param='11710'):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn.commit()

    user_cursor = sqlite3.connect('users.db').cursor()
    user_cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    user_cursor.execute('SELECT * from users')

    for data in user_cursor.fetchall():
        user, param = data[0], data[1]
        print(user, date_param, param)
        res_list = getData(param, date_param)
        msg = ''
        for r in res_list:
            try:
                cursor.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")' % (user, r))
            except sqlite3.IntegrityError:
                # 이미 해당 데이터가 있다는 것을 의미합니다.
                pass
            else:
                print(str(datetime.now()).split('.')[0], r)
                if len(r + msg) + 1 > MAX_MSG_LENGTH:
                    sendMessage(user, msg)
                    msg = r + '\n'
                else:
                    msg += r + '\n'
        if msg:
            sendMessage(user, msg)
    conn.commit()


if __name__ == '__main__':
    today = date.today()
    current_month = today.strftime('%Y%m')

    print('[', today, ']received token :', TOKEN)

    pprint(bot.getMe())

    run(current_month)
