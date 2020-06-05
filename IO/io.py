# -*- coding: utf-8 -*-

import pymysql.cursors
from slack import*
import winsound
import datetime
import time
import nfc

def flag():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='io',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "update flag_tb set flag=1"
    cursor.execute(sql)
    conn.commit()
    conn.close()

def checkFlag(): #登録システムを使用しているかチェックする関数
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='io',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "select * from flag_tb"
    cursor.execute(sql)
    flag = cursor.fetchone()
    conn.close()
    return flag['flag']

def IO(): #入退室の際のデータベース操作関数(一番大事)
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='io',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    #=====入退室する前の人数を取得=====================================================================
    cursor = conn.cursor()
    sql = "select count(*) from student_tb where STATUS='IN'"
    cursor.execute(sql)
    num = cursor.fetchone()
    _num = num['count(*)'] #入退室する前の人の数
    #=====ステータスの取得,更新=======================================================================
    sql = "select STATUS from student_tb where ID='"
    sql += str(id) + "'"
    cursor.execute(sql)
    io = cursor.fetchone()
    if str(io['STATUS']) == "OUT":
        color = "good"
        status = "入室"
        sql = "update student_tb set STATUS='IN' where ID='"
    else:
        color = "danger"
        status = "退室"
        sql = "update student_tb set STATUS='OUT' where ID='"
    sql += str(id) + "'"
    cursor.execute(sql)
    conn.commit()
    #=====ニックネームの取得=========================================================================
    sql = "select NICKNAME from student_tb where ID='"
    sql += str(id) + "'"
    cursor.execute(sql)
    nickname = cursor.fetchone()
    #=====入退室後の人数を取得=======================================================================
    sql = "select count(*) from student_tb where STATUS='IN'"
    cursor.execute(sql)
    num = cursor.fetchone()
    cursor.close()
    conn.close()
    #=====Slackへ通知==============================================================================
    if str(_num) == '0' and str(num['count(*)']) == '1': #もともと0人で、1人入ってきたらOPEN
        send_message_1("`---O P E N---`")
    send_message_0(color, nickname['NICKNAME'], status, num['count(*)'])
    if str(num['count(*)']) == '0': #0人になったらCLOSE
        send_message_1("`--C L O S E--`")

def connected(tag):
    global id #カードID
    global name #本名
    service_code = [nfc.tag.tt3.ServiceCode(0x100B >> 6, 0x100B & 0x3f)]
    bc_id = [nfc.tag.tt3.BlockCode(0)]
    bc_name = [nfc.tag.tt3.BlockCode(1)]
    name = tag.read_without_encryption(service_code, bc_name).decode()
    id = tag.read_without_encryption(service_code, bc_id).decode()

def Read():
    flag() #起動時に一応フラグを1にしておく
    print('===== T O U C H =====')
    latestID = ""
    latestTIME = 0
    while True:
        if checkFlag() == 1:
            try:
                with nfc.ContactlessFrontend('usb') as clf: #カードリーダーを探す
                    target_res = clf.sense(nfc.clf.RemoteTarget("212F"), iterations=1, interval=1) #反応を検知する
                    if not target_res is None:
                        tag = nfc.tag.activate(clf, target_res) #カードのタグを取得する
                        try:
                            connected(tag)
                            if id == latestID:
                                lag = datetime.datetime.now() - latestTIME #直近の入退室との差
                                waitTIME = 10 #同じIDの入退室は10秒間をおかないとできない
                                if lag.total_seconds() > waitTIME:
                                    winsound.Beep(2000, 400) #音を鳴らす
                                    IO() #入退室処理
                                    latestID = id #IDを更新
                                    latestTIME = datetime.datetime.now() #時間を更新
                                else:
                                    print("Please wait " + str(int(waitTIME-lag.total_seconds())+1) + " seconds")
                            else:
                                winsound.Beep(2000, 400) #音を鳴らす
                                IO() #入退室処理
                                latestID = id #IDを更新
                                latestTIME = datetime.datetime.now() #時間を更新
                        except:
                            print('error')
            except:
                pass


if __name__ == "__main__":
    Read()