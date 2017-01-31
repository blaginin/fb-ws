
from datetime import date, datetime, time

import sqlite3

import Logger
from python_mysql_dbconfig import read_config
# from user import user

class db:

    def __init__(self):
        try:

            db = read_config()
            self.conn = sqlite3.connect('database.sqlite')
            # self.conn = mysql.connector.connect(**db)
            self.cursor = self.conn.cursor()

        except BaseException as e:
            print(e)



    def getsubs(self, typeid):


            hour = datetime.now().hour

            datetimetocompare = time = datetime(2000,1,1,hour,0,0)

            query  = "SELECT UserID FROM Subscritions where enabled=1 and SubTime ='" + datetimetocompare.strftime('%Y-%m-%d %H:%M:%S') +"' and SubTypeId = " + str(typeid)

            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            fb_ids = []

            for row in rows:
                fb_ids.append(row[0])
            return fb_ids

    def createupdatesub(self,fb_ID, subtype, hour, enable):

        query  =  "SELECT * FROM Subscritions where UserID ="+fb_ID + " and SubTypeID=" + str(subtype)
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        time = datetime(2000,1,1,hour,0,0)

        if self.cursor.rowcount > 0:
            row_id = row[0]
            query = """ UPDATE Subscritions
                           SET SubTime = %s,
                               Enabled = %s
                           WHERE id = %s """

            args = (time, enable, row_id )


        else:
            query = "INSERT INTO Subscritions (UserID,SubTypeID,SubTime) VALUES( %s, 1, %s)"
            args = (fb_ID, time)

        try:

            self.cursor.execute(query, args)
            self.conn.commit()


        except BaseException as error:
            Logger.log(error)

    def createuser(self, fb_ID, FirstName = None, LastName = None, TimeZone = 3, LanguageId = 1):

        self.cursor.execute("SELECT * FROM users where ID =" + fb_ID)
        self.cursor.fetchone()

        if self.cursor.rowcount <= 0:
            query = "INSERT INTO users (ID, FirstName, LastName, TimeZone, LanguageID) VALUES( %s, %s, %s, %s, %s)"
            args = (fb_ID, FirstName, LastName, TimeZone, LanguageId )
            try:

                self.cursor.execute(query, args)
                self.conn.commit()

            except BaseException as error:
                Logger.log(error)
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
