from __future__ import division

import configure
import mysql.connector
import bitcoin
from decimal import *
from twisted.python.modules import getModule

class P2PminingData:
    def __init__(self):
        try:
            self.workDB = mysql.connector.connect(user=configure.db_username,password=configure.db_password,host=configure.db_location,database=configure.db_name)
            self.autocommit = False
            self.workDBcursor = self.workDB.cursor()
             
        except mysql.connector.Error as err:
            print(err)
        self.bitcoin = bitcoin.Bitcoin(configure.args)
    
    def add_shares(self,user,difficulty,on_time):
        try:
            self.workDBcursor.execute("""INSERT INTO live_shares (id,userid,shares) VALUES (NULL, %s , %s ) ON DUPLICATE KEY UPDATE shares=shares + %s""", (user[:36], difficulty * on_time, difficulty * on_time) )
            self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
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
                self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
            print(err)
    
    def record_p2pool_share(self,user,share_hash,on_time):
        try:
            self.workDBcursor.execute("INSERT INTO p2pool_shares (id,userid,share_hash,on_time,timestamp) VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())",(user[:36],share_hash,on_time))
            self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
            print(err)   
    
    def record_block_from_miner(self,user,block_hash,on_time):
        try:
            self.workDBcursor.execute("INSERT INTO found_blocks (id,userid,block_hash,on_time,timestamp) VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())",(user[:36],block_hash,on_time))
            self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
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
    
    def record_pool_rewards(self,blockhash):
        try:
            self.workDBcursor.execute("INSERT INTO pool_rewards_main (id,blockhash,timestamp) VALUES (NULL, %s , UNIX_TIMESTAMP() )", (blockhash,))
            self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
            print(err)
        self.get_rewards_trans_values()
        self.update_rewards_confirms()
        
    def get_rewards_trans_values(self):
        try:
            self.workDBcursor.execute("SELECT id,blockhash,value FROM pool_rewards_main WHERE `txid` = 'NONE'")
            result1 =  self.workDBcursor.fetchall()
            for (id,blockhash,value) in result1:
                txdata = self.bitcoin.get_reward_transaction(blockhash,configure.args.address)
                if txdata[0] is not None:
                    self.workDBcursor.execute("UPDATE pool_rewards_main SET txid = %s, value = %s WHERE id = %s",(txdata[0],txdata[1],id))
            self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
            print(err)
            
    def update_rewards_confirms(self):
        try:
            self.workDBcursor.execute("SELECT id,txid FROM pool_rewards_main WHERE confirmations < '120' AND txid != 'NONE'")
            result1 = self.workDBcursor.fetchall()
            for (id,txid) in result1:
                tx = self.bitcoin.get_transaction(txid)
                self.workDBcursor.execute("UPDATE pool_rewards_main SET confirmations = %s WHERE id = %s",(tx['confirmations'],id))
            self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
            print(err)
        
    #Distributes Rewards to Miners
    def distribute_rewards(self):
        try:
            
            self.workDBcursor.execute("SELECT id,value FROM pool_rewards_main WHERE distributed = '0' AND txid != 'NONE'")
            result1 = self.workDBcursor.fetchall()
            for (id,value) in result1:
                self.workDBcursor.execute("""SELECT SUM(shift_data.shares) as total_shares FROM shift_data, 
                (SELECT * FROM shifts ORDER BY timestamp DESC LIMIT %s) as payshift WHERE payshift.id = shift_data.shiftid""", (configure.shifts_pplns,))
                result2 = self.workDBcursor.fetchone()
                print "GOT TOTAL SHARES: %s" % (result2[0],)
                if result2[0] is not None:
                    self.workDBcursor.execute("""SELECT shift_data.id payid,shift_data.shares as sshares, payshift.id as shiftid FROM shift_data, 
                    (SELECT * FROM shifts ORDER BY timestamp DESC LIMIT %s) as payshift WHERE payshift.id = shift_data.shiftid""", (configure.shifts_pplns,))
                    print "GOT PAYMENTS"
                    result3=self.workDBcursor.fetchall()
                    for (payid, sshares,shiftid) in result3:
                        gross_value = (sshares/result2[0]) * value
                        pool_fee = gross_value * Decimal(configure.pool_fee / 100)
                        net_value = gross_value - pool_fee
                        self.workDBcursor.execute("""INSERT INTO miner_credits (id, rewardid, shiftid, shift_dataid, grossvalue, netvalue, timestamp, currency) 
                        VALUES (NULL, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(), 'BTC')""",(id,shiftid,payid,gross_value,net_value))
                        self.workDBcursor.execute("INSERT INTO pool_earnings (id, timestamp, miner_credits_id, fee) VALUES ( NULL,UNIX_TIMESTAMP(),%s,%s)",(cursor_insert.lastrowid,pool_fee))
                        print "INSERTED PAYMENTS"
                self.workDBcursor.execute("UPDATE pool_rewards_main SET distributed = '1' WHERE id = %s",(id,))
                self.workDB.commit()
        except mysql.connector.Error as err:
            self.workDB.rollback()
            print(err)    
       

