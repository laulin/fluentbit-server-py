import socketserver
import msgpack
import logging

class FluentbitRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        # print("create FluentRequestHandler")
        self._log = logging.getLogger("FluentbitRequestHandler")
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        # print("FluentRequestHandler.setup")
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        # print("FluentRequestHandler.handle")
        if self.server.get_authentication():
            auth = self.server.get_authentication()()
            authorized = auth.process_authentication(self.request)
        else:
            authorized = True

        if authorized:
            try:
                t = self.server.get_transport()()
                message_bin = t.collect(self.request)
                t.process(message_bin)
            except Exception as e:
                self._log.error("Drop message ({})".format(repr(e)))
                pass
        else:
            self._log.debug("Authentication failed")

    def finish(self):
        # print("FluentRequestHandler.finish")
        return socketserver.BaseRequestHandler.finish(self)