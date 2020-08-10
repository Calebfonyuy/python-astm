from astm.server import BaseRecordsDispatcher, Server

server = Server(dispatcher=BaseRecordsDispatcher, host='192.168.100.253', port=8000)
server.serve_forever()
