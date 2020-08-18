from datetime import datetime
from pathlib import Path
from shutil import move
from os import listdir
import re

"""
To control logging with command line commands, consider using 
sys.argv array to check what command line arguments have 
been provided.
"""


def server_log(info):
    log = str(datetime.now())+" Server: "+str(info)
    __write_log_file(log)
    print(log)


def client_log(info):
    log = str(datetime.now())+" Client: "+str(info)
    __write_log_file(log)
    print(log)


def common_log(info):
    log = str(datetime.now())+": "+str(info)
    __write_log_file(log)
    print(log)


def __write_log_file(log):
    file = open("astm_log.log",'a')
    file.write(log+"\n")
    file.close()
    path = Path('astm_log.log').stat()
    if path.st_size >=3000000:
        move('astm_log.log', "astm_log_"+str(datetime.now())+".log")
    today = datetime.now().day
    if day==1:
        month = datetime.now().month
        year = datetime.now().year
        all_logs = [f for f in os.listdir(".") if len(re.findall('[0-9- :.]+[0-9]+',str(f)))>0]
        
    

if __name__=="__main__":
    log = str(datetime.now())+" Client: Test Write"
    __write_log_file(log)