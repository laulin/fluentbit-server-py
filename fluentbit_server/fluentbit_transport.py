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


    def unpack_stream(self, data):
        # recursive data stream parsing
        while True:
            try:
                result = msgpack.unpackb(data, raw=True)
                yield result
                return
            except msgpack.exceptions.ExtraData as e:
                unpacked = e.unpacked
                data = e.extra
                yield unpacked
            except ValueError as e:
                self._log.warning("Drop {} bytes".format(len(data)))
                return

    def collect(self, request):
        """
        merge network packet to create a parsable message
        """

        data = b""
        request.settimeout(0.5)
        while True:

            try:
                new_block = request.recv(1024)
            except: 
                new_block = b""
            data += new_block
            
            if len(data) > self._buffer_size:
                raise BufferError("Message can't be bigger than {} bytes".format(self._buffer_size))

            if data[0] == b"{":
                raise NotImplementedError("JSON Message Mode is not implemented")
            else:
                if len(new_block) == 0:
                    for message in self.unpack_stream(data):
                        yield message
                    return

        return

    def process(self, message):

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
