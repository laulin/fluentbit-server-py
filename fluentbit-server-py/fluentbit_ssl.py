import ssl

class FluentbitSSL:
    def __init__(self, key_file, crt_file, verify=False):
        self._key_file = key_file
        self._crt_file = crt_file
        self._verify = verify

    def wrap(self, connection):
        cert_req = ssl.CERT_REQUIRED if self._verify else ssl.CERT_OPTIONAL
        output = ssl.wrap_socket(connection,
            server_side=True,
            certfile = self._crt_file,
            keyfile = self._key_file,
            ssl_version = ssl.PROTOCOL_TLS,
            cert_reqs = cert_req)
        return output