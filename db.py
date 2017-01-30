
from datetime import date, datetime, time
import mysql.connector
from mysql.connector import Error
import Logger
from python_mysql_dbconfig import read_config
from user import user

class db:

    def __init__(self):
        try:

            db = read_config()
            self.conn = mysql.connector.connect(**db)
            self.cursor = self.conn.cursor()

        except Error as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def getsubs(self, typeid):

            hour = datetime.now().hour

            datetimetocompare = time = datetime(2000, 1 , 1,hour,0,0)

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


        except Error as error:
            Logger.log(error)

    def createupdateuser(self,  fb_ID, WaitingForCommand, FirstName = None, LastName = None, TimeZone = None, LanguageId = 1, ):

        self.cursor.execute("SELECT * FROM users where ID =" + fb_ID)
        self.cursor.fetchone()

        if self.cursor.rowcount <= 0:
            query = "INSERT INTO users (ID, FirstName, LastName, TimeZone, LanguageID) VALUES( %s, %s, %s, %s, %s)"
            args = (fb_ID, FirstName, LastName, TimeZone, LanguageId )
        else:

            query = """ UPDATE users
                                       SET FirstName = %s,
                                           LastName = %s,
                                           TimeZone = %s,
                                           LanguageID = %s,
                                           WaitingForCommand = %s
                                       WHERE id = %s """
            args = ( FirstName, LastName, TimeZone, LanguageId, WaitingForCommand, fb_ID)
        try:

            self.cursor.execute(query, args)
            self.conn.commit()

        except Error as error:
            Logger.log(error)

    def getuserinfo(self, fb_ID):
        query = "SELECT * FROM users where ID =" + fb_ID
        self.cursor.execute(query)
        sqluser = self.cursor.fetchone()
        if self.cursor.rowcount > 0:
            return user(fb_id=fb_ID, FirstName=sqluser[1], LastName=sqluser[2], TimeZone=sqluser[3], LanguageID=sqluser[4], WaitingForCommand=sqluser[5])
        else:
            return None

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
    #a.testconn()
    user = a.getuserinfo('100006714724497')
    print (user)
