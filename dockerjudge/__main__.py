"WebSocket server"

from asyncio import get_event_loop, new_event_loop, set_event_loop
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from json import JSONEncoder as _JSONEncoder
from json import dumps, loads
from sys import argv

import websockets

from .main import judge
from .status import Status

executor = ThreadPoolExecutor()  # pylint: disable = E0012, consider-using-with


class JSONEncoder(_JSONEncoder):
    "TypeError: Object is not JSON serializable"

    def default(self, o):
        "bytes and dockerjudge.status.Status"
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, Status):
            return o.name
        return _JSONEncoder.default(self, o)


async def server(websocket, path):  # pylint: disable = W0613
    "WebSocket server"
    loop = get_event_loop()
    kwargs = loads(await websocket.recv())
    await websocket.send(dumps(["judge", kwargs]))
    kwargs["source"] = kwargs["source"].encode()
    kwargs["tests"] = [(i.encode(), o.encode()) for i, o in kwargs["tests"]]
    kwargs["config"]["callback"] = {
        "compile": lambda *args: loop.create_task(
            websocket.send(dumps(["compile", args], cls=JSONEncoder))
        )
    }
    res = await loop.run_in_executor(executor, partial(judge, **kwargs))
    await websocket.send(dumps(["done", res], cls=JSONEncoder))


def main(*args):
    "if __name__ == '__main__'"
    set_event_loop(new_event_loop())

    start_server = websockets.serve(server, *args)

    get_event_loop().run_until_complete(start_server)
    get_event_loop().run_forever()


if __name__ == "__main__":
    try:
        main(*argv[1].split(":"))
    except KeyboardInterrupt:
        print()
