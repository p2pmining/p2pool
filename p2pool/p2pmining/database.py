import configure
import mysql.connector

class P2PminingData:
    def __init__(self):
        try:
            self.workDB = mysql.connector.connect(user=configure.db_username,password=configure.db_password,host=configure.db_location,database=configure.db_name)
            self.workDBcursor = self.workDB.cursor()
            print 'HELLO'
        except mysql.connector.Error as err:
            print(err)
    
    def add_shares(self,user,difficulty,on_time):
        try:
            self.workDBcursor.execute("""INSERT INTO live_shares (id,userid,shares) VALUES (NULL, %s , %s ) ON DUPLICATE KEY UPDATE shares=shares + %s""", (user, difficulty * on_time, difficulty * on_time) )
        except mysql.connector.Error as err:
            print(err)