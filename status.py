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
from MySpamMethods import getarticles
from flask import render_template
import time

def status():
	database = db()
	active = 0
	disabled = 0

	try:
		u = database.testconn()
		active 		= len(database.cursor.execute("SELECT * FROM Subscritions WHERE enabled=1").fetchall())
		disabled 	= len(database.cursor.execute("SELECT * FROM Subscritions WHERE enabled=0").fetchall())
		opt = "Ok"
	except BaseException as e: 
		opt = 'Failed ('+str(e)+')'
	
	next_horos = getarticles('http://podruga.top/rss')
	next_horo = next_horos[0].title

	BOT = {
		'header' : 'Гороскопы',
		'url':'https://www.messenger.com/t/chocolady.club',
		'data':{\
			'Состояние БД' : opt,
			'Количество подписанных' : active,
			'Количество отписавшихся' : disabled,
			'Количество кандидатов на ближайшую рассылку':len(next_horos),
			'Хэдер кандидата':next_horo
		}
	}



	return render_template("status.html",
        time = time.strftime("%H:%M"),
        bots = [BOT]
        )


	return """
	Active users: {0}<br>
	Disabled users: {1}<br>

	next horo: {2}<br>
	""".format(active, disabled, next_horo), 200

