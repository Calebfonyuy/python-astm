# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
import sys
sys.path.insert(1, "../")
import logging
import socket
from .asynclib import Dispatcher, loop
from .codec import decode_message, is_chunked_message, join
from .constants import ACK, CRLF, EOT, NAK, ENCODING
from .exceptions import InvalidState, NotAccepted
from .protocol import ASTMProtocol
from .logging import server_log
from orm.models import Header, ResultatAutomate, find_automate
from orm.result_params import params


log = logging.getLogger(__name__)

__all__ = ['BaseRecordsDispatcher', 'RequestHandler', 'Server']


class BaseRecordsDispatcher(object):
    """Abstract dispatcher of received ASTM records by :class:`RequestHandler`.
    You need to override his handlers or extend dispatcher for your needs.
    For instance::

        class Dispatcher(BaseRecordsDispatcher):

            def __init__(self, encoding=None):
                super(Dispatcher, self).__init__(encoding)
                # extend it for your needs
                self.dispatch['M'] = self.my_handler
                # map custom wrappers for ASTM records to their type if you
                # don't like to work with raw data.
                self.wrapper['M'] = MyWrapper

            def on_header(self, record):
                # initialize state for this session
                ...

            def on_patient(self, record):
                # handle patient info
                ...

            # etc handlers

            def my_handler(self, record):
                # handle custom record that wasn't implemented yet by
                # python-astm due to some reasons
                ...

    After defining our dispatcher, we left only to let :class:`Server` use it::

        server = Server(dispatcher=Dispatcher)
    """

    #: Encoding of received messages.
    encoding = ENCODING

    def __init__(self, encoding=None):
        server_log("Server: Initiating request dispatcher")
        self.encoding = encoding or self.encoding
        self.dispatch = {
            'H': self.on_header,
            'Q': self.on_query,
            'C': self.on_comment,
            'P': self.on_patient,
            'O': self.on_order,
            'R': self.on_result,
            'M': self.on_information,
            'L': self.on_terminator
        }
        self.wrappers = {}
        self.active_header = None
        self.order_id = None
        server_log("Request dispatcher initialization complete")

    def __call__(self, message):
        server_log("In __call__ method of request dispatcher with message {}".format(message))
        seq, records, cs = decode_message(message, self.encoding)
        for record in records:
            print(record[0])
            # self.dispatch.get(record[0], self.on_unknown)(self.wrap(record))
            self.dispatch.get(record[0], self.on_unknown)(record)

    def wrap(self, record):
        server_log("Wrapping record "+record)
        rtype = record[0]
        if rtype in self.wrappers:
            return self.wrappers[rtype](*record)
        return record

    def _default_handler(self, record):
        server_log(f"Ignoring processing of record {record}")
        log.warning('Record remains unprocessed: %s', record)

    def on_header(self, record):
        """Header record handler."""
        server_log("Processing header record {}".format(record))
        self.active_header = Header(record)
        self.order_id = None
        server_log(self.active_header.log())
        server_log("Completed header handling")

    def on_query(self, record):
        """Query record handler."""
        server_log("Processing query record {}".format(record))
        self._default_handler(record)

    def on_comment(self, record):
        """Comment record handler."""
        server_log("Processing comment record {}".format(record))
        self._default_handler(record)

    def on_patient(self, record):
        """Patient record handler."""
        server_log("Processing patient record {}".format(record))
        self._default_handler(record)

    def on_order(self, record):
        """Order record handler."""
        server_log("Processing order record {}".format(record))
        if self.order_id:
            raise NotAccepted("Not expecting New order record at this moment")
        self.order_id = record[2]
        self._default_handler(record)

    def on_result(self, record):
        """Result record handler."""
        server_log("Processing result record {}".format(record))
        #result = ResultatAutomate(
        #    automate=self.active_header.automate,
        #    code=self.order_id,
        #    id_rendu=params[record[2][3]],
        #    valeur=record[3],
        #    nom_rendu=record[2][3]
        #)
        self._default_handler(record)

    def on_terminator(self, record):
        """Terminator record handler."""
        server_log("Closing query handling")
        self.active_header = None

    def on_information(self, record):
        """Information record handler."""
        server_log("Processing information record {}".format(record))
        self._default_handler(record)

    def on_unknown(self, record):
        """Fallback handler for dispatcher."""
        server_log("Processing unknown record {}".format(record))
        self._default_handler(record)


class RequestHandler(ASTMProtocol):
    """ASTM protocol request handler.

    :param sock: Socket object.

    :param dispatcher: Request handler records dispatcher instance.
    :type dispatcher: :class:`BaseRecordsDispatcher`

    :param timeout: Number of seconds to wait for incoming data before
                    connection closing.
    :type timeout: int
    """
    def __init__(self, sock, dispatcher, timeout=None):
        super(RequestHandler, self).__init__(sock, timeout=timeout)
        self._chunks = []
        host, port = sock.getpeername() if sock is not None else (None, None)
        server_log(f"Initiating Client handler for {host}:{port}")
        self.client_info = {'host': host, 'port': port}
        self.dispatcher = dispatcher
        self._is_transfer_state = False
        self.terminator = 1
        server_log(f"Client handler initiation for {host}:{port} complete")

    def on_enq(self):
        server_log(f"ENQ received from {self.client_info['host']}:{self.client_info['port']}")
        if not self._is_transfer_state:
            self._is_transfer_state = True
            self.terminator = [CRLF, EOT]
            server_log(f"ENQ handle from {self.client_info['host']}:{self.client_info['port']} complete")
            return ACK
        else:
            log.error('ENQ is not expected')
            server_log(f"Unexpected ENQ from {self.client_info['host']}:{self.client_info['port']}")
            return NAK

    def on_ack(self):
        server_log(f"ACK received from {self.client_info['host']}:{self.client_info['port']}")
        raise NotAccepted('Server should not be ACKed.')

    def on_nak(self):
        server_log(f"ACK received from {self.client_info['host']}:{self.client_info['port']}")
        raise NotAccepted('Server should not be NAKed.')

    def on_eot(self):
        server_log(f"EOT received from {self.client_info['host']}:{self.client_info['port']}")
        if self._is_transfer_state:
            self._is_transfer_state = False
            self.terminator = 1
            server_log(f"EOT handle from {self.client_info['host']}:{self.client_info['port']} complete")
        else:
            server_log(f"Unexpected EOT received from {self.client_info['host']}:{self.client_info['port']}")
            raise InvalidState('Server is not ready to accept EOT message.')

    def on_message(self):
        server_log(f"Message(ETX) received from {self.client_info['host']}:{self.client_info['port']}")
        if not self._is_transfer_state:
            server_log(f"Unexpected ETX received from {self.client_info['host']}:{self.client_info['port']}")
            self.discard_input_buffers()
            return NAK
        else:
            try:
                self.handle_message(self._last_recv_data)
                server_log(f"ETX handling from {self.client_info['host']}:{self.client_info['port']} complete")
                return ACK
            except Exception:
                server_log(f"Error handling ETX from {self.client_info['host']}:{self.client_info['port']}: {self._last_recv_data}")
                log.exception('Error occurred on message handling.')
                return NAK

    def handle_message(self, message):
        server_log(f"handling message from {self.client_info['host']}:{self.client_info['port']} : {message.decode()}")
        self.is_chunked_transfer = is_chunked_message(message)
        if self.is_chunked_transfer:
            self._chunks.append(message)
        elif self._chunks:
            self._chunks.append(message)
            self.dispatcher(join(self._chunks))
            self._chunks = []
        else:
            self.dispatcher(message)

    def discard_input_buffers(self):
        server_log(f"Discarding input buffers for {self.client_info['host']}:{self.client_info['port']}")
        self._chunks = []
        return super(RequestHandler, self).discard_input_buffers()

    def on_timeout(self):
        """Closes connection on timeout."""
        server_log(f"Connection timeout for {self.client_info['host']}:{self.client_info['port']}")
        super(RequestHandler, self).on_timeout()
        self.close()

    def handle_close(self):
        super(RequestHandler, self).handle_close()
        server_log(f"{self.client_info['host']}:{self.client_info['port']} disconnected")


class Server(Dispatcher):
    """Asyncore driven ASTM server.

    :param host: Server IP address or hostname.
    :type host: str

    :param port: Server port number.
    :type port: int

    :param request: Custom server request handler. If omitted  the
                    :class:`RequestHandler` will be used by default.

    :param dispatcher: Custom request handler records dispatcher. If omitted the
                       :class:`BaseRecordsDispatcher` will be used by default.

    :param timeout: :class:`RequestHandler` connection timeout. If :const:`None`
                    request handler will wait for data before connection
                    closing.
    :type timeout: int

    :param encoding: :class:`Dispatcher <BaseRecordsDispatcher>`\'s encoding.
    :type encoding: str
    """

    request = RequestHandler
    dispatcher = BaseRecordsDispatcher

    def __init__(self, host='localhost', port=15200,
                 request=None, dispatcher=None,
                 timeout=None, encoding=None):
        super(Server, self).__init__()
        server_log("Started Server Initiation")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        server_log("Server Socket Created")
        self.set_reuse_addr()
        self.bind((host, port))
        server_log("Server address binding complete")
        self.listen(5)
        self.pool = []
        self.timeout = timeout
        self.encoding = encoding
        if request is not None:
            self.request = request
        if dispatcher is not None:
            self.dispatcher = dispatcher
        server_log("Server Initiation complete")

    def handle_accept(self):
        server_log("Accepting new Connection")
        pair = self.accept()
        if pair is None:
            server_log("Connection failed")
            return
        sock, addr = pair
        server_log("New connection established with {}".format(addr))
        self.request(sock, self.dispatcher(self.encoding), timeout=self.timeout)
        server_log(f"Client handler for {addr} created")
        super(Server, self).handle_accept()
        server_log("Client connection complete")

    def serve_forever(self, *args, **kwargs):
        """Enters into the :func:`polling loop <asynclib.loop>` to let server
        handle incoming requests."""
        server_log("Server now awaiting connections.....")
        loop(*args, **kwargs)
