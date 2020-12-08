import sys
import logging

from fluentbit_authentication import FluentbitAuthentication
from fluentbit_transport import FluentbitTransport
from fluentbit_request_handler import FluentbitRequestHandler
from fluentbit_server import FluentbitServer
from fluentbit_ssl import FluentbitSSL
from functools import partial

authentication_factory = partial(FluentbitAuthentication, shared_key="my_shared_key", server_hostname="server.com")
transport_factory = partial(FluentbitTransport, callback=print)
ssl = FluentbitSSL(key_file="etc/toto.com.key", crt_file="etc/toto.com.cert")


def main():
    logging.basicConfig(level=logging.DEBUG)

    server = FluentbitServer(("localhost", 24000), FluentbitRequestHandler, transport_factory, authentication_factory, ssl)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError:
        print("Socket in use")
    finally:
        server.server_close()
        print("closed")
        sys.exit(0)

if __name__ == "__main__":
    main()