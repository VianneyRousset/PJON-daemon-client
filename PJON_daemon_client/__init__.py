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

import PJON_daemon_client.protocol as proto
import asyncio

__author__ = "Vianney Rousset"
__license__ = "GPL3"
__version__ = "1.0.0"
__maintainer__ = "Vianney ROusset"
__status__ = "Beta"


class CommunicationError(Exception):
    pass


async def _connect(socket_path):
    reader, writer = await asyncio.open_unix_connection('\0' + socket_path)
    # checking protocol version
    return reader, writer
    p = proto.read_packet(await reader.readexactly(proto.PACKET_SIZE))
    if (not isinstance(p, proto.PacketVersion)):
        raise CommunicationError(f'Excepted {proto.PacketVersion} received '
                                 f'{type(p)}')
    if (p.version != proto.VERSION):
        raise CommunicationError('Wrong protocol version (excepted: '
                                 f'"{proto.VERSION}", got: "{p.version}")')
    return reader, writer


async def listen(socket_path='/tmp/PJON.sock'):
    reader, _ = await _connect(socket_path)
    while True:
        yield proto.read_packet(await reader.readexactly(proto.PACKET_SIZE))


async def send(dest, data, socket_path='/tmp/PJON.sock'):
    reader, writer = await _connect(socket_path)
    writer.write(proto.PacketOutgoingMessage(dest, data).to_buffer())

    while True:
        p = proto.read_packet(await reader.read(proto.PACKET_SIZE))
        if isinstance(p, proto.PacketError):
            if p.code is proto.Error.RECEIVED_INVALID_PACKET_HEAD:
                raise CommunicationError('Server received invalid packet head')
        if isinstance(p, proto.PacketOutgoingResult):
            writer.close()
            return p.result
