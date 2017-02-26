# -*- coding: utf-8 -*-

from datetime import datetime
import FaceBookHelper
from db import db
from Article import Article
import Logger
import urllib
import xml.etree.ElementTree as ET
bot_db = db()
import json 

def spamsample():
    subtypes_list = [1]
    for i in subtypes_list:
        article_list = getarticles('http://podruga.top/rss')
        Logger.log(len(article_list))
        person_id_list = list(set(bot_db.getsubs(i)))
        print("+ person_id_list", person_id_list)
        for person_id in person_id_list:
            for article in article_list:
                a = FaceBookHelper.send_articles_message(person_id, article)
                a = a.json()
                                
                if 'error' in a.keys():
                    if a['error']['code'] == 200 and a['error']['error_subcode'] == 1545041:
                        bot_db.createupdatesub(person_id, 1, 0, 0)
                        print('[deleted]', person_id)






def getarticles(url):
    articlelist = []
    rss = urllib.request.urlopen(url).read()  
    root = ET.fromstring(rss)
    root = root[0]
    for item in root.findall('item'):
        for category in item.findall('category'):
            if "ЕДНЕВНЫЙ ГОРОСКОП" in category.text.upper():
                date = datetime.strptime(" ".join(item.find("pubDate").text.split()[1:-1]), '%d %b %Y %H:%M:%S')
                if date.date() == datetime.now().date() : 
                    desc = item.find('description').text
                    announce = desc.replace('\n', ' ')[:200] + "..."
                    title = item.find("title").text
                    image_url = getImage(desc)
                    link = item.find("link").text
                    articlelist.append(Article(title, announce, link, image_url, date))
                break
    return articlelist


def getImage(desc):
    image_url = ""
    search_string = '<img src="'
    img_start_position = desc.find(search_string)
    if img_start_position>0:
        img_length = desc[img_start_position+len(search_string)+1:].find('class')
        if img_length > 0:
            image_url = desc[img_start_position:img_start_position+img_length+10].split('"')[1]
    return image_url


if __name__ == '__main__':
   # app.run(debug=True)
    l = getarticles("http://podruga.top/rss")
    print(len(l))
