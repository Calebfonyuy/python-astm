from datetime import datetime

"""
To control logging with command line commands, consider using 
sys.argv array to check what command line arguments have 
been provided.
"""


def server_log(info):
    print(datetime.now(), "Server:", info)


def client_log(info):
    print(datetime.now(), "Client", info)


def common_log(info):
    print(datetime.now(), info)
