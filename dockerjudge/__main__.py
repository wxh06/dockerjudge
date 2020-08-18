'WebSocket server'

import asyncio
from concurrent.futures import ThreadPoolExecutor
from json import JSONEncoder as _JSONEncoder, dumps, loads
from sys import argv

import websockets
from .main import judge as _judge
from .status import Status

executor = ThreadPoolExecutor()


class JSONEncoder(_JSONEncoder):
    'TypeError: Object is not JSON serializable'
    def default(self, o):
        'bytes and dockerjudge.status.Status'
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, Status):
            return o.name
        return _JSONEncoder.default(self, o)


def judge(kwargs):
    'Return _judge(**kwargs)'
    return _judge(**kwargs)


async def hello(websocket, path):  # pylint: disable = W0613
    'hello'
    loop = asyncio.get_event_loop()
    kwargs = loads(await websocket.recv())
    await websocket.send(dumps(['judge', kwargs]))
    kwargs['source'] = kwargs['source'].encode()
    kwargs['tests'] = [(i.encode(), o.encode()) for i, o in kwargs['tests']]
    kwargs['config']['callback'] = {
        'compile': lambda *args: loop.create_task(
            websocket.send(dumps(['compile', args], cls=JSONEncoder))
        )
    }
    res = await loop.run_in_executor(executor, judge, kwargs)
    await websocket.send(dumps(['done', res], cls=JSONEncoder))

start_server = websockets.serve(hello, *argv[1].split(':'))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
