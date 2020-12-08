import unittest
import msgpack
import struct
from pprint import pprint
from collections import namedtuple
import logging

Event = namedtuple("Event", ["tag", "timestamp", "record"])

class FluentbitTransport:
    def __init__(self, callback:object, buffer_size=32*1024):
        # callback is a function with one argument : the event to be processed
        self._callback = callback
        self._buffer_size = buffer_size
        self._log = logging.getLogger("FluentbitTransport")

    def collect(self, request):
        """
        merge network packet to create a parsable message
        """
        ok = False
        data = b""
        while not ok:
            data += request.recv(1024)
            if len(data) > self._buffer_size:
                raise BufferError("Message can't be bigger than {} bytes".format(self._buffer_size))
            try:
                if data[0] == b"{":
                    raise NotImplementedError("JSON Message Mode is not implemented")
                else:
                    msgpack.unpackb(data, raw=True)
                    ok = True
            except NotImplementedError as e:
                raise e
            except:
                pass
                
        return data

    def process(self, message_bin):
        self._log.debug(message_bin)
        if message_bin[0] == b'{':
            # message as json, not supported
            raise NotImplementedError("JSON Message Mode is not implemented")

        message = msgpack.unpackb(message_bin, raw=True)
        output = []
        if isinstance(message[1], int):
            # Message mode
            raise NotImplementedError("Message Mode is not implemented")
        elif isinstance(message[1], list):
            # forward
            output = self.forward_mode(message)
        elif isinstance(message[1], str) or  isinstance(message[1], bytes):
            # PackedForward Mode or CompressedPacketForward Mode
            raise NotImplementedError("PackedForward Mode or CompressedPacketForward Mode are not implemented")

        for e in output:
            self._callback(e)

        return        

    def forward_mode(self, message):
        tag = message[0]
        output = []
        for entry in message[1]:
            tmp = Event(tag, *self.parse_entry(entry))
            output.append(tmp)

        return output

    def parse_entry(self, entry):
        if isinstance(entry[0], msgpack.ext.ExtType):
            second, nanosecond = struct.unpack("!II", entry[0].data)
        else:
            second, nanosecond = int(entry[0]), 0
        record = entry[1]

        return (second + nanosecond/1000000.0, record)


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

        callback.result = list()

        ft = FluentbitTransport(callback)
        ft.process(message_bin)

        expected = [Event(b'random.0', 1607338098.884014, {b'rand_value': 12619388134949588322}),
                    Event(b'random.0', 1607338096.877777, {b'rand_value': 14315931674231618647}),
                    Event(b'random.0', 1607338096.88848, {b'rand_value': 6736132637168392508}),
                    Event(b'random.0', 1607338101.094242, {b'rand_value': 17960168518128249560}),
                    Event(b'random.0', 1607338098.223275, {b'rand_value': 1152785846868949817})]

        self.assertEqual(callback.result, expected)

        

