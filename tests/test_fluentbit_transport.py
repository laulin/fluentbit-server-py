import unittest
import msgpack
from fluentbit_server.fluentbit_transport import FluentbitTransport, Event

class TestFluentbitTransport(unittest.TestCase):
    def test_forward_mode(self):
        message_bin = b'\x92\xa8random.0\x95\x92\xd7\x00_\xce\x07\xa5\x0cE\x8an\x81\xaarand_value\xcf\xaf!\x12\xa5\xfas\rb\x92\xd7\x00_\xce\x07\xa6\x0c\x17\xabQ\x81\xaarand_value\xcf\xc6\xach\x027V\xbcW\x92\xd7\x00_\xce\x07\xa7\x0c\x08\x92\xe0\x81\xaarand_value\xcf]{\x8c\xf1\xa6VY<\x92\xd7\x00_\xce\x07\xa8\x0c9}b\x81\xaarand_value\xcf\xf9?V\x1c50*\xd8\x92\xd7\x00_\xce\x07\xa9\x0b\xfelk\x81\xaarand_value\xcf\x0f\xff\x84\x9e\xb8\xb8\xbb9'
        message = msgpack.unpackb(message_bin, raw=True)

        ft = FluentbitTransport(None)
        result = ft.forward_mode(message)

        expected = [Event(b'random.0', 1607338098.884014, {b'rand_value': 12619388134949588322}),
                    Event(b'random.0', 1607338096.877777, {b'rand_value': 14315931674231618647}),
                    Event(b'random.0', 1607338096.88848, {b'rand_value': 6736132637168392508}),
                    Event(b'random.0', 1607338101.094242, {b'rand_value': 17960168518128249560}),
                    Event(b'random.0', 1607338098.223275, {b'rand_value': 1152785846868949817})]

        self.assertEqual(result, expected)

    def test_process(self):
        message_bin = b'\x92\xa8random.0\x95\x92\xd7\x00_\xce\x07\xa5\x0cE\x8an\x81\xaarand_value\xcf\xaf!\x12\xa5\xfas\rb\x92\xd7\x00_\xce\x07\xa6\x0c\x17\xabQ\x81\xaarand_value\xcf\xc6\xach\x027V\xbcW\x92\xd7\x00_\xce\x07\xa7\x0c\x08\x92\xe0\x81\xaarand_value\xcf]{\x8c\xf1\xa6VY<\x92\xd7\x00_\xce\x07\xa8\x0c9}b\x81\xaarand_value\xcf\xf9?V\x1c50*\xd8\x92\xd7\x00_\xce\x07\xa9\x0b\xfelk\x81\xaarand_value\xcf\x0f\xff\x84\x9e\xb8\xb8\xbb9'
        def callback(event):
            callback.result.append(event)

        message = msgpack.unpackb(message_bin, raw=True)

        callback.result = list()

        ft = FluentbitTransport(callback)
        ft.process(message)

        expected = [Event(b'random.0', 1607338098.884014, {b'rand_value': 12619388134949588322}),
                    Event(b'random.0', 1607338096.877777, {b'rand_value': 14315931674231618647}),
                    Event(b'random.0', 1607338096.88848, {b'rand_value': 6736132637168392508}),
                    Event(b'random.0', 1607338101.094242, {b'rand_value': 17960168518128249560}),
                    Event(b'random.0', 1607338098.223275, {b'rand_value': 1152785846868949817})]

        self.assertEqual(callback.result, expected)

        

