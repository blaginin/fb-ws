# -*- coding: utf-8 -*-
import sys
import json
import requests
import Logger
from db import db
from flask import Flask, request
from python_mysql_dbconfig import read_config
import urllib
import xml.etree.ElementTree as ET
from datetime import datetime

from Article import Article


def getImage(desc):

    image_url = ""

    search_string = '<img src="'

    img_start_position = desc.find(search_string)
    if img_start_position>0:
        img_length = desc[img_start_position+len(search_string)+1:].find('class')
        if img_length > 0:
            image_url = desc[img_start_position:img_start_position+img_length+10].split('"')[1]

    return image_url


time_string = "TIME"
PAGE_ACCESS_TOKEN = read_config(section="facebook")["page_access_token"]

def asktime(user):
    qr = [{"content_type":"text",
        "title":str(i),
        "payload":"SET_TIME_"+str(i)}

        for i in range(0, 24)
    ]
    send_message(user, "Укажи, сколько сейчас часов в месте, где ты находишься. Я определю твой часовой пояс и буду присылать гороскопы вовремя ;)", additional={"quick_replies":qr})

def webhook_handler():
    data = request.get_json()
    # Logger.log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:

            for messaging_event in entry["messaging"]:

                sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message


                #print('msg', messaging_event.get("message"), messaging_event.get("postback"), messaging_event.get("postback"))
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    command = messaging_event["postback"]["payload"].strip()
                    # #print('\tpayload:', command, command=="DEVELOPER_DEFINED_LAST")

                    if command == "DEVELOPER_DEFINED_SUBSCRIBE":
                        subscribe_time_menu(sender_id , '1')

                    elif command == "DEVELOPER_DEFINED_LAST":
                        # send_message(sender_id, "Вот последняя новость с сайта http://podruga.top")
                        art = fetch_last_news()
                        send_articles_message(sender_id, art)


                    elif command == "DEVELOPER_DEFINED_UNSUBSCRIBE":

                        bot_db = db()
                        bot_db.createupdatesub(fb_ID=sender_id,subtype=1, hour=0, enable=0)
                        send_message(sender_id, "Подписка отменена :( Возвращайтесь")

                    elif command == "DEVELOPER_DEFINED_ABOUT":
                        send_message(sender_id, "Я - бот. Умею каждый день присылать гороскоп и актуальные новости. Давай общаться ;)")


                    elif command.upper().find(time_string) == 0:
                        bot_db = db()
                        utc = bot_db.createuser(sender_id)
                        hours = int(command.split(';')[1])
                        bot_db.createupdatesub(fb_ID=sender_id,subtype=1, hour=hours, enable=1)


                        qr = {"quick_replies":[\
                          {
                            "content_type":"text",
                            "title":"Читать новости",
                            "payload":"DEVELOPER_DEFINED_LAST"
                          },]}

                        send_message(sender_id, "Ура! :) Подписка оформлена. Гороскопы будут приходить в {0}:00".format(hours), additional=qr)
                    else:
                        send_message(sender_id, command)



                elif messaging_event.get("message"):  # someone sent us a message

                    # recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    try:
                        message_text = ''
                        if "text" in messaging_event["message"]:  # the message's text
                            message_text = messaging_event["message"]["text"]
                        
                        Logger.log('[{0}]: `{1}`'.format(sender_id, message_text))

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
                        elif 'НОВОС' in message_text.upper():
                            # send_message(sender_id, "Вот последняя новость с сайта http://podruga.top")
                            art = fetch_last_news()
                            send_articles_message(sender_id, art)



                        else:

                            send_message(sender_id, "Что? Для настройки подписки пиши `гороскоп`. Настройки доступны в меню.")
                        # send_image(sender_id, "http://xiostorage.com/wp-content/uploads/2015/10/test.png")
                    except Exception as e:
                        #common_main_menu(sender_id)
                        send_message(sender_id, e.message)
                        #Logger.log(e.message)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

    return "ok", 200


def fetch_last_news():
    url = 'http://podruga.top/rss'
    articlelist = []

    rss = urllib.request.urlopen(url).read()  
    root = ET.fromstring(rss)

    root = root[0]
    for item in root.findall('item'):
        desc = item.find('description').text
        announce = desc.split('\n')[0].split('<')[0][:200] + "..."
        title = item.find("title").text
        date = datetime.strptime(" ".join(item.find("pubDate").text.split()[1:-1]), '%d %b %Y %H:%M:%S')
        image_url = getImage(desc)
        link = item.find("link").text


        return (Article(title, announce, link, image_url, date))


def send_message(recipient_id, message_text, additional={}):
        #Logger.log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        toj = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        }

        if 'quick_replies' in additional.keys():
            toj['message']['quick_replies'] = additional['quick_replies']

        data = json.dumps(toj)


        return send_json(data, headers, params)

def send_image(recipient_id, picture_url):
        #Logger.log("sending message to {recipient}: {url}".format(recipient=recipient_id, url=picture_url))

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
        return send_json(data, headers, params)

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
                                    "subtitle": "В удобное тебе время.",
                                    "buttons": [
                                        # {
                                        #     "type": "web_url",
                                        #     "url": "http://podruga.top",
                                        #     "title": "О нас"
                                        # },
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
                                    "subtitle": "Каждый день в удобное для тебя время.",
                                    "buttons": [
                                        # {
                                        #     "type": "web_url",
                                        #     "url": "http://podruga.top",
                                        #     "title": "О нас"
                                        # },
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

        return send_json(data, headers, params)

def subscribe_menu(recipient_id):
        #Logger.log("subscribe_menu start")

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

        return send_json(data, headers, params)

def subscribe_time_menu(recipient_id, sub_type):
        #Logger.log("subscribe_menu start")

        send_message(recipient_id, "Для того, чтобы каждый день получать гороскоп, тебе нужно подписаться. Я буду отправлять новости в этот диалог.")



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

        return send_json(data, headers, params)

def send_json(data, headers, params):
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            Logger.log(r.text)
        return r

def send_articles_message(recipient_id, article):

    #Logger.log("sending articles to {recipient}".format(recipient=recipient_id))
    if not article.article_url.endswith('?utm_medium=bot'):
        article.article_url+='?utm_medium=bot'

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
                        "title":"Читать"
                      }
                    ]
                  }
                ]
              }
            },
          
            "quick_replies":[
      {
        "content_type":"text",
        "title":"Еще новости",
        "payload":"DEVELOPER_DEFINED_LAST"
      },]


        }

    })
    return send_json(data, headers, params)
