import msgpack
import hashlib
from fluentbit_server.fluentbit_authentication import FluentbitAuthentication

import unittest

class TestFluentbitAuthentication(unittest.TestCase):
    def test_create_salt(self):
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
