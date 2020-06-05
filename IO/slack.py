# -*- coding: utf-8 -*-

import slackweb

#slack=slackweb.Slack(url="https://hooks.slack.com/services/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") #20入退室
slack = slackweb.Slack(url="https://hooks.slack.com/services/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") # test-ap(debug)

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