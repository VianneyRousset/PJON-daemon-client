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

import client
import asyncio

ID_COMPUTER = 0x42
ID_UNO = 0x22
ID_NANO = 0x33


async def main():
    done, _ = await asyncio.wait([send(), listen()],
                                 return_when='FIRST_EXCEPTION')
    done, pending = done.__iter__().__next__()
    done.cancel()
    print('>>> ', done.exception())
    e = done.exception()
    try:
        for p in pending:
            p.cancel()
    except BaseException as e:
        print(f'Failed to cancel pending tasks: {e}')
        if e:
            raise e


async def send():
    while True:
        await asyncio.sleep(0.1)
        print(await client.send(ID_NANO, b'salut'))


async def listen():
    async for p in client.listen():
        print(p)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
