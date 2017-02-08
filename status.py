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


def status():
	database = db()

	active 		= len(database.cursor.execute("SELECT * FROM Subscritions WHERE enabled=1").fetchall())
	disabled 	= len(database.cursor.execute("SELECT * FROM Subscritions WHERE enabled=0").fetchall())

	next_horo = getarticles('http://podruga.top/rss')[0].title

	return """
	Active users: {0}<br>
	Disabled users: {1}<br>

	next horo: {2}<br>
	""".format(active, disabled, next_horo), 200

