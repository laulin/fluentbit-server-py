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
