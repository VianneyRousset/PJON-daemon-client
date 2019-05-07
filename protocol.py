#!/usr/bin/env python

'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


from struct import unpack, pack, calcsize
from enum import Enum


PACKET_SIZE = 64
VERSION = '0.0.1'


class Head(Enum):
    VERSION         = 0x00
    INFO            = 0x01
    WARN            = 0x02
    ERROR           = 0x03
    INGOING_MSG     = 0x04
    OUTGOING_MSG    = 0x05
    OUTGOING_RESULT = 0x06


class Error(Enum):
    FAILED_OPEN_SERIAL              = 0x01
    RECEIVED_INVALID_PACKET_HEAD    = 0x02


class Warn(Enum):
    pass


class Info(Enum):
    SERIAL_OPENED   = 0x01


class OutgoingResult(Enum):
    SUCCESS             = 0x00
    INTERNAL_ERROR      = 0x01
    CONTENT_TOO_LONG    = 0x02
    CONNECTION_LOST     = 0x03


class UnexpectedHeader(Exception):

    def __init__(self, expected, got):
        msg = f'Expected: {expected} got: {got}'
        super().__init__(msg)


class InvalidCstring(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class InternalError(Exception):

    def __int__(self, msg):
        super().__init__(msg)


class Packet:

    def __init__(self, head=None):
        self.head = head
        self._head_format = '=B'

    def from_buffer(self, buf):
        self.head = self.__read_head(buf)

    def to_buffer(self):
        buf = pack(self._head_format, self.head.value)
        return self._pad(buf)

    def _read_c_string(self, buf):
        index = buf.find(b'\0')
        if (index < 0):
            raise InvalidCstring(f'No end of string found in: {buf}')
        return bytes(buf[:index]).decode('ascii')

    def _pad(self, buf):
        if (len(buf) > PACKET_SIZE):
            raise InternalError("Packet overflow (excepting "
                                f"{PACKET_SIZE}, got: {len(buf)})")
        padding = bytearray(PACKET_SIZE - len(buf))
        return self._check(buf + padding)

    def _check(self, buf):
        if len(buf) != PACKET_SIZE:
            raise InternalError("Invalid packet size (excepting "
                                f"{PACKET_SIZE}, got: {len(buf)})")
        return buf

    def __read_head(self, buf):
        code = unpack(self._head_format, buf[:calcsize(self._head_format)])[0]
        return Head(code)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__}>'


class PacketVersion(Packet):

    def __init__(self, version=None):
        super().__init__(Head.VERSION)
        self._packet_format = self._head_format
        self.version = version

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.VERSION):
            raise UnexpectedHeader(Head.VERSION, self.head)
        self.version = self._read_c_string(buf[calcsize(self._head_format):])

    def to_buffer(self):
        buf = pack(self._packet_format, self.head.value, self.code)
        return self._pad(buf)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'version: {self.version}>'


class PacketInfo(Packet):

    def __init__(self, code=None):
        super().__init__(Head.INFO)
        self._packet_format = self._head_format + 'H'
        self.code = code

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.INFO):
            raise UnexpectedHeader(Head.INFO, self.head)
        fmt = self._packet_format
        _, code = unpack(fmt, buf[:calcsize(fmt)])
        self.code = Info(code)

    def to_buffer(self):
        buf = pack(self._packet_format, self.head.value, self.code)
        return self._pad(buf)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'code: {self.code}>'


class PacketWarn(Packet):

    def __init__(self, code=None):
        super().__init__(Head.WARN)
        self._packet_format = self._head_format + 'H'
        self.code = code

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.WARN):
            raise UnexpectedHeader(Head.WARN, self.head)
        fmt = self._packet_format
        _, code = unpack(fmt, buf[:calcsize(fmt)])
        self.code = Warn(code)

    def to_buffer(self):
        buf = pack(self._packet_format, self.head.value, self.code)
        return self._pad(buf)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'code: {self.code}>'


class PacketError(Packet):

    def __init__(self, code=None):
        super().__init__(Head.ERROR)
        self._packet_format = self._head_format + 'H'
        self.code = code

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.ERROR):
            raise UnexpectedHeader(Head.ERROR, self.head)
        fmt = self._packet_format
        _, code = unpack(fmt, buf[:calcsize(fmt)])
        self.code = Error(code)

    def to_buffer(self):
        buf = pack(self._packet_format, self.head.value, self.code)
        return self._pad(buf)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'code: {self.code}>'


class PacketIngoingMessage(Packet):

    def __init__(self, src=None, data=bytearray()):
        super().__init__(Head.INGOING_MSG)
        self._packet_format = self._head_format + 'BH'
        self.src = src
        self.data = data

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.INGOING_MSG):
            raise UnexpectedHeader(Head.ERROR, self.head)
        fmt = self._packet_format
        _, self.src, length = unpack(fmt, buf[:calcsize(fmt)])
        buf = buf[calcsize(fmt):]
        self.data = buf[:length]

    def to_buffer(self):
        buf = pack(self._packet_format, self.head.value, self.src,
                   len(self.data))
        return self._pad(buf + self.data)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'src: 0x{self.src:02x}, length: {len(self.data)}>'


class PacketOutgoingMessage(Packet):

    def __init__(self, dest=None, data=bytearray()):
        super().__init__(Head.OUTGOING_MSG)
        self._packet_format = self._head_format + 'BH'
        self.dest = dest
        self.data = data

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.INGOING_MSG):
            raise UnexpectedHeader(Head.ERROR, self.head)
        fmt = self._packet_format
        _, self.dest, length = unpack(fmt, buf[:calcsize(fmt)])
        buf = buf[calcsize(fmt):]
        self.data = buf[:length]

    def to_buffer(self):
        buf = pack(self._packet_format, self.head.value, self.dest,
                   len(self.data))
        return self._pad(buf + self.data)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'dest: 0x{self.dest:02x}, length: {len(self.data)}>'


class PacketOutgoingResult(Packet):

    def __init__(self, result=None):
        super().__init__(Head.OUTGOING_RESULT)
        self._packet_format = self._head_format + 'H'
        self.result = result

    def from_buffer(self, buf):
        super().from_buffer(buf)
        if (self.head is not Head.OUTGOING_RESULT):
            raise UnexpectedHeader(Head.OUTGOING_RESULT, self.head)
        fmt = self._packet_format
        _, result = unpack(fmt, buf[:calcsize(fmt)])
        self.result = OutgoingResult(result)

    def to_buffer(self):
        buf = pack(self._packet_format, self.result)
        return self._pad(buf + self.data)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} - ' \
            f'result: {self.result}>'


def read_packet(buf):
    p = Packet()
    p.from_buffer(buf)
    p = {Head.VERSION: PacketVersion,
         Head.INFO: PacketInfo,
         Head.WARN: PacketWarn,
         Head.ERROR: PacketError,
         Head.INGOING_MSG: PacketIngoingMessage,
         Head.OUTGOING_MSG: PacketOutgoingMessage,
         Head.OUTGOING_RESULT: PacketOutgoingResult}[p.head]()
    p.from_buffer(buf)
    return p
