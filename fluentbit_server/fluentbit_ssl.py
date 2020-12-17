import ssl
import os.path

class FluentbitSSL:
    def __init__(self, key_file, crt_file, verify=False):
        self._context = self.create_context(key_file, crt_file, verify)

    def create_context(self, key_file, crt_file, verify):
        if not os.path.isfile(key_file):
            raise IOError("Key file {} doesn't exist".format(key_file))

        if not os.path.isfile(crt_file):
            raise IOError("Certificat file {} doesn't exist".format(crt_file))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_REQUIRED if verify else ssl.CERT_OPTIONAL
        context.load_cert_chain(crt_file, key_file)

        return context

    def wrap(self, connection):
        output = self._context.wrap_socket(connection, server_side=True)

        return output