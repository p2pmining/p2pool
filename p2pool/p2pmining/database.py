import configure
import mysql.connector
from twisted.python.modules import getModule

class P2PminingData:
    def __init__(self):
        try:
            self.workDB = mysql.connector.connect(user=configure.db_username,password=configure.db_password,host=configure.db_location,database=configure.db_name)
            self.workDBcursor = self.workDB.cursor()
            
        except mysql.connector.Error as err:
            print(err)
    
    def add_shares(self,user,difficulty,on_time):
        try:
            self.workDBcursor.execute("""INSERT INTO live_shares (id,userid,shares) VALUES (NULL, %s , %s ) ON DUPLICATE KEY UPDATE shares=shares + %s""", (user[:36], difficulty * on_time, difficulty * on_time) )
        except mysql.connector.Error as err:
            print(err)
    
    def check_for_shift_completion(self):
        try:
            self.workDBcursor.execute("SELECT sum(shares) AS share_total FROM live_shares")
            returned = self.workDBcursor.fetchone()
            if (0 if returned[0] is None else int(returned[0])) > configure.shares_per_shift:
                self.workDBcursor.execute("SELECT * FROM live_shares")
                returned = self.workDBcursor.fetchall()
                self.workDBcursor.execute("INSERT INTO shifts (id, timestamp, shiftpay, lastblockheight, confirmed) VALUES (NULL, UNIX_TIMESTAMP(), '0', '0', FALSE)")
                shift_id = self.workDBcursor.lastrowid
                for row in returned:
                    self.workDBcursor.execute("INSERT INTO shift_data (id,userid,shares,shiftid) VALUES (NULL, %s, %s, %s)", (row[1],row[2],shift_id))
                self.workDBcursor.execute("UPDATE live_shares SET shares = '0'")
        except mysql.connector.Error as err:
            print(err)
    
    def record_p2pool_share(self,user,share_hash,on_time):
        try:
            self.workDBcursor.execute("INSERT INTO p2pool_shares (id,userid,share_hash,on_time,timestamp) VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())",(user[:36],share_hash,on_time))
        except mysql.connector.Error as err:
            print(err)   
    
    def record_block_from_miner(self,user,block_hash,on_time):
        try:
            self.workDBcursor.execute("INSERT INTO found_blocks (id,userid,block_hash,on_time,timestamp) VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())",(user[:36],block_hash,on_time))
        except mysql.connector.Error as err:
            print(err)
    
    def close(self):
        self.workDBcursor.close()
        self.workDB.close()
        
    def run_sql_from_file(self,filename):
        moduleDirectory = getModule(__name__).filePath.parent()
        fd = moduleDirectory.child(filename).open()
        sqlFile = fd.read()
        fd.close()
        sqlCommands = sqlFile.split(';')
        for command in sqlCommands:
            try:
                self.workDBcursor.execute(command)
            except mysql.connector.Error as err:
                print "Command skipped: ", err
                
    def setup_database(self):
        self.run_sql_from_file('p2pmining_database.sql')

