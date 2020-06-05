# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, url_for
import pymysql.cursors
from slack import*
import winsound
import time
import nfc
import os

app = Flask(__name__)

def ChangeFlag(flag): #入退室との競合を防ぐための関数
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='io',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "update flag_tb set flag="
    sql += str(flag)
    cursor.execute(sql)
    conn.commit()
    conn.close()

def insert(): #データベースに学生データを挿入する関数
    conn = pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='io',
                                charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "delete from student_tb where ID='"
    sql += id + "'"
    cursor.execute(sql)
    sql = "insert into student_tb values('"
    sql += str(id) + "','"
    sql += str(name) + "','"
    sql += str(nickname) + "','"
    sql += "OUT')"
    cursor.execute(sql)
    conn.commit()
    conn.close()

def reset(): #強制退室のための関数
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='io',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "update student_tb set STATUS='OUT' where STATUS='IN'"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    send_message_1("`--R E S E T--`")

def connected(tag):
    global id
    global name
    service_code = [nfc.tag.tt3.ServiceCode(0x100B >> 6, 0x100B & 0x3f)]
    bc_id = [nfc.tag.tt3.BlockCode(0)]
    bc_name = [nfc.tag.tt3.BlockCode(1)]
    name = tag.read_without_encryption(service_code, bc_name).decode()
    id = tag.read_without_encryption(service_code, bc_id).decode()

def Read():
    ChangeFlag(0) #フラグの切り替え(0なら登録,1なら入退室)
    time.sleep(1) #入れといたほうがいいかも
    while True:
        try:
            with nfc.ContactlessFrontend('usb') as clf: #カードリーダーを探す
                target_res = clf.sense(nfc.clf.RemoteTarget("212F"), iterations=1, interval=1) #反応を検知する
                if not target_res is None:
                    tag = nfc.tag.activate(clf, target_res) #カードのタグを取得する
                    try:
                        connected(tag)
                        insert() #学生データを挿入
                        result = "success" #登録成功
                        break
                    except:
                        result = "failure" #登録失敗
                        break
        except:
            result = "error" #カードリーダーの読み込み失敗
            break
    ChangeFlag(1) #フラグの切り替え(0なら登録,1なら入退室)
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def regist():
    global nickname
    nickname = request.form['nickname']
    try:
        if nickname == "reset":
            reset()
            return render_template('result.html', result="R E S E T")
        result = Read()
        if result == "success":
            return render_template('result.html', result="S U C C E S S", message = 'Register as ' + '"' + nickname + '"')
        elif result == "failure":
            return render_template('result.html', result="F A I L U R E")
        else:
            return render_template('result.html', result="E R R O R", message="Reconnect the card reader")
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run()