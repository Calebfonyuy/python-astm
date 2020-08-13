from astm.server import RequestHandler, BaseRecordsDispatcher, Server

server = Server(dispatcher=BaseRecordsDispatcher, host='192.168.100.253', port=8080)
server.serve_forever()
