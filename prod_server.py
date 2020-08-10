from astm.server import RequestHandler, BaseRecordsDispatcher, Server

server = Server(dispatcher=BaseRecordsDispatcher, host='127.0.0.1', port=8000)
server.serve_forever()
