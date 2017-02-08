
from datetime import date, datetime, time

import sqlite3

import Logger
from python_mysql_dbconfig import read_config
# from user import user


def process_sql(st):
	DELETE = '`', "'", '"', 'select', 'delete', 'where'
	stu = st.upper()
	for row in DELETE:
		row = row.upper()
		q = None
		try:
			q = stu.index(row)
			print('!', q)
			st = st[:q] + '*'*len(row) + st[q+len(row):]
		except ValueError:
			pass
	return st

class db:

    def __init__(self):
        try:
            db = read_config()
            self.conn = sqlite3.connect('database.sqlite')
            # self.conn = mysql.connector.connect(**db)
            self.cursor = self.conn.cursor()

        except IndexError as e:
            print(e)



    def getsubs(self, typeid, hour=None):
            self.__init__()
            print('getsubs', hour)
            if hour is None:    
                hour = (datetime.utcnow().hour + 3)%24 #MSK

            if hour == 'any':
                query  = "SELECT UserID FROM Subscritions where enabled=1 "

            else:
                datetimetocompare = time = datetime(2000,1,1,hour,0,0)
                query  = "SELECT UserID FROM Subscritions where enabled=1 and SubTime ='" + datetimetocompare.strftime('%Y-%m-%d %H:%M:%S') +"' and SubTypeId = " + str(typeid)
            

            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            fb_ids = []

            for row in rows:
                fb_ids.append(row[0])
            return fb_ids

    def createupdatesub(self,fb_ID, subtype, hour, enable):

        query  =  "SELECT * FROM Subscritions where UserID ="+str(process_sql(fb_ID)) + " and SubTypeID=" + str(subtype)
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        time = datetime(2000,1,1,hour,0,0).strftime('%Y-%m-%d %H:%M:%S')


        query = "INSERT or REPLACE INTO Subscritions (UserID,SubTypeID,SubTime,Enabled) VALUES( {0}, 1, '{1}', {2})".format(fb_ID, time, enable)

        try:
            print('QU', query)
            self.cursor.execute(query)
        except IndexError as error:
            Logger.log(error)

        
        self.conn.commit()


    def createuser(self, fb_ID, FirstName = None, LastName = None, TimeZone = 3, LanguageId = 1):

        self.cursor.execute("SELECT * FROM users where ID =" + fb_ID)
        self.cursor.fetchone()
        FirstName, LastName, TimeZone, LanguageId, map(process_sql, map(str, (FirstName, LastName, TimeZone, LanguageId)))

        if self.cursor.rowcount <= 0:
            query = "REPLACE INTO users (ID, FirstName, LastName, TimeZone, LanguageID) VALUES( {0}, '{1}', '{2}', {3}, {4})".format(fb_ID, FirstName, LastName, TimeZone, LanguageId)
            try:
                print('QU', query)
                self.cursor.execute(query)
            except IndexError as error:
                Logger.log(error)

            
            self.conn.commit()

        return TimeZone

    def testconn(self):
        self.cursor.execute("SELECT * FROM users")
        row = self.cursor.fetchone()
        print(row)

    def issub(self, fb_ID, subtype):
        query = "SELECT * FROM Subscritions where enabled=1 and UserID =" + fb_ID + " and SubTypeID=" + str(subtype)
        self.cursor.execute(query)
        self.cursor.fetchone()
        return self.cursor.rowcount > 0



if __name__ == '__main__':
    a = db()
    a.testconn()
    #a.createuser('100006714724497','Ilya','Kuskov')
    #a.createupdatesub('100006714724497',1,12,1)
    #for i in a.getsubs(1):
    #    print (i)
