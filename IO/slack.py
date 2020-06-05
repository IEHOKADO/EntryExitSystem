# -*- coding: utf-8 -*-

import slackweb

slack = channel_url

def send_message_0(color,nickname,status,num): #複数行送信
    try:
        attachments = []
        attachment = {"color": str(color),
                      "title": str(status),
                      #"pretext": "",
                      "text": str(nickname) + " さんが" + str(status) + "されました。\n現在_" + str(num) + "_人です。",
                      "mrkdwn_in": ["text", "pretext"]}
        attachments.append(attachment)
        slack.notify(attachments = attachments)
        print("send_message")
    except:
        print("can't_send_message")

def send_message_1(status): #一行送信
    try:
        slack.notify(text=status)
        print(status)
    except:
        print(status)
