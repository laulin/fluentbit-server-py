import ssl

class FluentbitSSL:
    def __init__(self, key_file, crt_file, verify=False):
        self._key_file = key_file
        self._crt_file = crt_file
        self._verify = verify

    def wrap(self, connection):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_REQUIRED if self._verify else ssl.CERT_OPTIONAL
        context.load_cert_chain(self._crt_file, self._key_file)

        output = context.wrap_socket(connection, server_side=True)

        return output