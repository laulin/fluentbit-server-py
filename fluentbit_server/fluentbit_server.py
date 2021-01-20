import socketserver
import logging

class FluentbitServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class, transport, authentication=None, ssl=None):
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        self._authentication = authentication
        self._transport = transport
        self._ssl = ssl
        self._log = logging.getLogger("FluentbitServer")
        return

    def server_activate(self):
        socketserver.TCPServer.server_activate(self)
        return

    def server_close(self):
        self.shutdown()
        return socketserver.TCPServer.server_close(self)

    def get_request(self):
        try:
            newsocket, fromaddr = self.socket.accept()
        except  Exception as e:
            self._log.error("Failed to accept socket " + repr(e))
            return None, None

        if self._ssl:
            try:
                return self._ssl.wrap(newsocket), fromaddr
            except Exception as e:
                self._log.error("Failed to wrap socket " + repr(e))
                return None, None
        else:
            return newsocket, fromaddr

    def verify_request(self, request, client_address):
        """
        return False if the socket failed
        """

        if request is None or client_address is None:
            return False

        return True

    def shutdown_request(self, request):
        try:
            socketserver.TCPServer.shutdown_request(self, request)
        except Exception as e:
            self._log.error("Failed to shutdown socket ({})".format(repr(e)))

    def get_authentication(self): return self._authentication
    def get_transport(self): return self._transport