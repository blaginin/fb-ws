# -*- coding: utf-8 -*-

import Logger
import urllib2
#import xml.etree.ElementTree as ET
import json






def getresult(url, searchString):

    searchresultlist = []

    with open('1.json') as json_data:
        d = json.load(json_data)
        for i in d["items"]:
            searchresultlist.append(i)

    #rss = urllib2.urlopen(url).read()

    #data = json.loads(json1)


    return searchresultlist


