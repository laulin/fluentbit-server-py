import msgpack
import hashlib
from uuid import uuid4
import logging

import unittest

class FluentbitAuthentication:
    # use https://github.com/fluent/fluentd/wiki/Forward-Protocol-Specification-v1
    def __init__(self, shared_key:str, server_hostname:str):
        self._shared_key = shared_key
        self._server_hostname = server_hostname
        self._nonce = self.create_salt() 
        self._auth = self.create_salt()
        self._shared_key_salt = b"" # from the client
        self._log = logging.getLogger("FluentbitAuthentication")

    def process_authentication(self, request):
        # request is an object that expect following interface :
        # - recv
        # - sendall

        request.sendall(self.create_HELO())
        self._log.debug("HELO sent")

        ping_bin = request.recv(1024)
        self._log.debug("PING received, parsing ...")
        try:
            result = self.validate_PING(ping_bin)
        except Exception as e :
            self._log.debug("Exception in validate PING : {}".format(e))
            result = (False, "unknow")
        self._log.debug("PING parsing result is {}".format(result))
        
        request.sendall(self.create_PONG(*result))
        self._log.debug("PONG sent")

        return result[0]

    def create_HELO(self):
        response = [
            "HELO",
            {
                "nonce": self._nonce,
                "auth": self._auth,
                "keepalive": True
            }
        ]

        response_bin = msgpack.packb(response)
        return response_bin

    def validate_PING(self, ping_bin):
        # b'\x96\xa4PING\xa4plop\xb0\xeb\x0f\xde\xd4h5/<@\xcc^\xdb\xae\xfa\xab\xeb\xd9\x80a1911c227ed186b39b167e3fbf5719d9c80a237da565b4f62dd6e286ffb37ceb187b613ca50493d34517223404064fdff994a6f8b6a1733f6251c84991af2c79\xa0\xd9\x807c39875506b13517d397cae1fc000b42b9eac87d912dc43ac02f3d3e779a72cc81bf0f90b5c7e9c2bb03bb8b87f4d69e4d1da88750484bb20d71909db8525e7b'
        ping = msgpack.unpackb(ping_bin, raw=True)

        message_type = ping[0]
        if message_type != b"PING":
            return (False, "bad message type")
        
        client_hostname = ping[1] # unused
        self._shared_key_salt = ping[2]
        shared_key_hexdigest = ping[3]
        own_shared_key_hexdigest = hashlib.sha512(self._shared_key_salt + client_hostname + self._nonce + self._shared_key.encode("ascii")).hexdigest().encode("utf8")
        if shared_key_hexdigest != own_shared_key_hexdigest:
            return (False, "bad shared key")

        # /!\ user/password not supported since it is designed for fluentbit

        return (True, "")

    def create_PONG(self, auth:bool, reason:str):
        hostname = ""
        shared_key_hashed = ""
        if auth:
            hostname = self._server_hostname
            shared_key_hashed = hashlib.sha512(self._shared_key_salt + hostname.encode("ascii") + self._nonce + self._shared_key.encode("ascii")).hexdigest()
        response = [
            "PONG",
            auth,
            reason,
            hostname,
            shared_key_hashed
        ]
        return msgpack.packb(response)

    def create_salt(self):
        salt1 = uuid4().hex.encode("ascii")
        salt2 = uuid4().hex.encode("ascii")
        return hashlib.sha512(salt1 + salt2).digest()


class TestFluentbitAuthentication(unittest.TestCase):
    def test_cerate_salt(self):
        fa = FluentbitAuthentication("", "")
        result = fa.create_salt()
        self.assertEqual(len(result), 512/8)

    def test_create_HELO(self):
        fa = FluentbitAuthentication("", "")
        fa.create_HELO()

    def test_create_PONG_ok(self):
        fa = FluentbitAuthentication("my_key", "toto.com")
        result = fa.create_PONG(True, "")

        self.assertEqual(len(result), 147)

    def test_create_PONG_ko(self):
        fa = FluentbitAuthentication("my_key", "toto.com")
        result = fa.create_PONG(False, "Bad key !")
        self.assertEqual(len(result), 19)
    
    def test_validate_PING_OK(self):
        shared_key = "my_shared_key"
        shared_salt = b"salt_xxxxxxxxxxxxxxxx"
        client_host = b"client.com"

        fa = FluentbitAuthentication(shared_key, "server.com")
        helo = msgpack.unpackb(fa.create_HELO())
        nonce = helo[1]["nonce"]
        ping_message = [
            b"PING",
            client_host,
            shared_salt,
            hashlib.sha512(shared_salt + client_host + nonce + shared_key.encode("ascii")).hexdigest()
        ]
        ping_bin = msgpack.packb(ping_message)
        result = fa.validate_PING(ping_bin)
        self.assertEqual(result[0], True)
