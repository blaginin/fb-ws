# -*- coding: utf-8 -*-
import sys
import json
import requests
import Logger
from db import db
from flask import Flask, request
from python_mysql_dbconfig import read_config



time_string = "TIME"
PAGE_ACCESS_TOKEN = read_config(section="facebook")["page_access_token"]

def webhook_handler():
    data = request.get_json()
    #Logger.log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:

            for messaging_event in entry["messaging"]:

                sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message

                if messaging_event.get("message"):  # someone sent us a message

                    # recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    try:
                        message_text = ''
                        if "text" in messaging_event["message"]:  # the message's text
                            message_text = messaging_event["message"]["text"]
                    # send_message(sender_id, "press the buttons")
                        if (
                              message_text.upper().find("START")>=0
                           or message_text.upper().find("HI")>=0
                           or message_text.upper().find("HELLO")>=0
                           or message_text.upper().find("МЕНЮ")>= 0
                           or message_text.upper().find("ПРИВ")>=0
                           or message_text.upper().find("ПИСК") >= 0
                           or message_text.upper().find("ГОРОСКОП") >= 0

                        ):
                            common_main_menu(sender_id)
                        else:
                            send_message(sender_id, "Спасибо за отзыв :)")
                        # send_image(sender_id, "http://xiostorage.com/wp-content/uploads/2015/10/test.png")
                    except Exception as e:
                        #common_main_menu(sender_id)
                        send_message(sender_id, e.message)
                        Logger.log(e.message)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    command = messaging_event["postback"]["payload"]
                    if command == "DEVELOPER_DEFINED_SUBSCRIBE":
                        subscribe_time_menu(sender_id , '1')
                    elif command == "DEVELOPER_DEFINED_UNSUBSCRIBE":

                        bot_db = db()
                        bot_db.createupdatesub(fb_ID=sender_id,subtype=1, hour=0, enable=0)
                        send_message(sender_id, "Подписка отменена :( Возвращайтесь")

                    elif command.upper().find(time_string) == 0:
                        bot_db = db()
                        utc = bot_db.createuser(sender_id)
                        hours = int(command.split(';')[1]) - utc
                        bot_db.createupdatesub(fb_ID=sender_id,subtype=1, hour=hours, enable=1)
                        #.createupdatesub()
                        send_message(sender_id, "Ура! :) Подписка оформлена")
                    else:
                        send_message(sender_id, command)

    return "ok", 200

def send_message(recipient_id, message_text):
        Logger.log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        })
        send_json(data, headers, params)

def send_image(recipient_id, picture_url):
        Logger.log("sending message to {recipient}: {url}".format(recipient=recipient_id, url=picture_url))

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": picture_url
                    }
                }
            }
        })
        send_json(data, headers, params)

def common_main_menu(recipient_id):

        bot_db = db()
        issub = bot_db.issub(recipient_id, '1')

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        if issub:
            data = json.dumps({
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": [
                                {
                                    "title": "Привет, я могу присылать тебе Ежедневный гороскоп \"Шоколадное настроение\" ",
                                    #"item_url": "https://petersfancybrownhats.com",
                                    #"image_url": "https://petersfancybrownhats.com/company_image.png",
                                    "subtitle": "в удобное тебе время и скоро научусь еще многому. Напиши, чем бы еще я могла быть тебе полезна",
                                    "buttons": [
                                        {
                                            "type": "web_url",
                                            "url": "http://podruga.top",
                                            "title": "О нас"
                                        },
                                        {
                                            "type": "postback",
                                            "title": "Отписаться",
                                            "payload": "DEVELOPER_DEFINED_UNSUBSCRIBE"
                                        },
                                    ]
                                }
                            ]
                        }
                    }
                }
            })
        else:
            data = json.dumps({
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": [
                                {
                                    "title": "Привет, я могу присылать тебе Ежедневный гороскоп \"Шоколадное настроение\" ",
                                    # "item_url": "https://petersfancybrownhats.com",
                                    # "image_url": "https://petersfancybrownhats.com/company_image.png",
                                    "subtitle": "в удобное тебе время и скоро научусь еще многому. Напиши, чем бы еще я могла быть тебе полезна",
                                    "buttons": [
                                        {
                                            "type": "web_url",
                                            "url": "http://podruga.top",
                                            "title": "О нас"
                                        },
                                        {
                                            "type": "postback",
                                            "title": "Подписаться",
                                            "payload": "DEVELOPER_DEFINED_SUBSCRIBE"
                                        },
                                    ]
                                }
                            ]
                        }
                    }
                }
            })

        send_json(data, headers, params)

def subscribe_menu(recipient_id):
        Logger.log("subscribe_menu start")

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Выбери тип подписки",
                                #"item_url": "https://petersfancybrownhats.com",
                                #"image_url": "https://petersfancybrownhats.com/company_image.png",
                                #""subtitle": "Можешь попросить мне присылать тебе интересующие тебя вещи, например, гороскопы",
                                "buttons": [
                                    {
                                        "type": "postback",
                                        "title": "Гороскоп",
                                        "payload": "DEVELOPER_DEFINED_SUBSCRIBE_G"
                                    },
                                    {
                                        "type": "postback",
                                        "title": "Рецепты",
                                        "payload": "DEVELOPER_DEFINED_SUBSCRIBE_R"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        })

        send_json(data, headers, params)

def subscribe_time_menu(recipient_id, sub_type):
        Logger.log("subscribe_menu start")

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Во сколько присылать?",
                                #"item_url": "https://petersfancybrownhats.com",
                                #"image_url": "https://petersfancybrownhats.com/company_image.png",
                                #""subtitle": "Можешь попросить мне присылать тебе интересующие тебя вещи, например, гороскопы",
                                "buttons": [
                                    {
                                        "type": "postback",
                                        "title": "8-00",
                                        "payload": time_string+";8;"+ sub_type
                                    },
                                    {
                                        "type": "postback",
                                        "title": "10-00",
                                        "payload": time_string+";10;" + sub_type
                                    },
                                    {
                                        "type": "postback",
                                        "title": "12-00",
                                        "payload": time_string+";12;" + sub_type
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        })

        send_json(data, headers, params)

def send_json(data, headers, params):
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            Logger.log(r.status_code)
            Logger.log(r.text)

def send_articles_message(recipient_id, article):

    Logger.log("sending articles to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient":{
            "id": recipient_id
  },
          "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"generic",
                "elements":[
                  {
                    "title": article.title,
                    "item_url": article.article_url,
                    "image_url": article.image_url ,
                    "subtitle": article.announce,
                    "buttons":[
                      {
                        "type":"web_url",
                        "url": article.article_url,
                        "title":"Читать далее ->"
                      }
                    ]
                  }
                ]
              }
            }
          }
    })
    send_json(data, headers, params)
