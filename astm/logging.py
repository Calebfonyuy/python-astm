from datetime import datetime


def server_log(info):
    print(datetime.now(), "Server:", info)


def client_log(info):
    print(datetime.now(), "Client", info)


def common_log(info):
    print(datetime.now(), info)
