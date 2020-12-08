import socketserver

class FluentbitServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class, transport, authentication=None, ssl=None):
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        self._authentication = authentication
        self._transport = transport
        self._ssl = ssl
        return

    def server_activate(self):
        socketserver.TCPServer.server_activate(self)
        return

    def server_close(self):
        self.shutdown()
        return socketserver.TCPServer.server_close(self)

    def get_request(self):
        newsocket, fromaddr = self.socket.accept()

        if self._ssl:
            try:
                return self._ssl.wrap(newsocket), fromaddr
            except Exception as e:
                print(repr(e))
        else:
            return newsocket, fromaddr

    def get_authentication(self): return self._authentication
    def get_transport(self): return self._transport