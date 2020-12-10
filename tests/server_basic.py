import sys
import logging

from fluentbit_server.fluentbit_authentication import FluentbitAuthentication
from fluentbit_server.fluentbit_transport import FluentbitTransport
from fluentbit_server.fluentbit_request_handler import FluentbitRequestHandler
from fluentbit_server.fluentbit_server import FluentbitServer
from fluentbit_server.fluentbit_ssl import FluentbitSSL
from functools import partial

transport_factory = partial(FluentbitTransport, callback=print)


def main():
    logging.basicConfig(level=logging.DEBUG)

    server = FluentbitServer(("localhost", 24000), FluentbitRequestHandler, transport_factory)

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