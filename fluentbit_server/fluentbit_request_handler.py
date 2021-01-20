import socketserver
import msgpack
import logging

class FluentbitRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self._log = logging.getLogger("FluentbitRequestHandler")
        self._log.debug("Init for {}".format(client_address))
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        self._log.debug("setup")
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        self._log.debug("handle")
        if self.server.get_authentication():
            try:
                auth = self.server.get_authentication()()
                authorized = auth.process_authentication(self.request)
            except Exception as e:
                self._log.error("Authentication failed ({})".format(repr(e)))
                return
        else:
            authorized = True

        if authorized:
            try:
                t = self.server.get_transport()()
                for message_bin in t.collect(self.request):
                    t.process(message_bin)
            except Exception as e:
                self._log.error("Drop message ({})".format(repr(e)))
        else:
            self._log.debug("Authentication failed (refused)")

    def finish(self):
        self._log.debug("finish")
        return socketserver.BaseRequestHandler.finish(self)