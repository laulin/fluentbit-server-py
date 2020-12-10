# Fluentbit-server-py

Fluentd and Fluentbit are two great tools, like swiss knife. You can gather data, work on them and ship them to another FluentX instance. But what happen when you want to ship them to a Python program ? You need to do a workaround based on files, or stuff like that.

Well, that why it exists : if you need to gather data from fluentbit and process them in a python program (AI, exotic database, ...), you need that lib.

It implements a partial version for the *forward protocol* (https://github.com/fluent/fluentd/wiki/Forward-Protocol-Specification-v1):

* SSL support
* authentication based on shared_key
* transport *forward mode* only

This library is designed as server for Fluentbit and was not tested on Fluentd (maybe it works ?).

# Example


```python 
import sys
import logging

from fluentbit_server.fluentbit_authentication import FluentbitAuthentication
from fluentbit_server.fluentbit_transport import FluentbitTransport
from fluentbit_server.fluentbit_request_handler import FluentbitRequestHandler
from fluentbit_server.fluentbit_server import FluentbitServer
from fluentbit_server.fluentbit_ssl import FluentbitSSL
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
```

Authentication and ssl are optionals so such line will product a basic server (no authentication, no ciphering):

```python 

server = FluentbitServer(("localhost", 24000), FluentbitRequestHandler, transport_factory)

```

# Licence

This software is under MIT. 