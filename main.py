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


async def main(n=1):
    done, _ = await asyncio.wait([send(n), listen()],
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


async def send(n):
    import time
    while True:
        print('Sending')
        tic = time.process_time()
        done, pending = await asyncio.wait([client.send(ID_NANO, b'salut')
                                            for i in range(n)])
        try:
            for p in pending:
                print('ERROR: still pending futures -> cancelling')
                p.cancel()
        except BaseException as e:
            print(f'Failed to cancel pending tasks: {e}')

        for f in done:
            print(f.result())
        print('sent {} msg in {:.2f}s'.format(n, time.clock() - tic))
        await asyncio.sleep(1)
        return


async def listen():
    async for p in client.listen():
        print(p)


if __name__ == "__main__":
    from sys import argv
    n = 1 if len(argv) < 2 else int(argv[1])
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(n))
    finally:
        loop.close()
