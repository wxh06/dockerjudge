'dockerjudge - A Docker Based Online Judge Engine'

from concurrent.futures import ThreadPoolExecutor
from pathlib import PurePosixPath

import docker

from .dockerpy import exec_run, put_bin
from . import processor as _processor
from .status import Status
from . import test_case

__version__ = '1.3.1'


def judge(processor, source, tests, config=None,
          client=docker.from_env()):
    """Main function

    :param processor: Programming language processor
    :type processor:
        :class:`dockerjudge.processor.Processor`, `list` or `tuple`
    :param source: Source code
    :type source: str
    :param tests: Test cases
    :type tests: list
    :param config: Configuration

        +------------------------------+-----------------+---------+----------+
        | Key                          | Description     | Default |Value type|
        +================+=============+=================+=========+==========+
        | ``callback``   | ``compile`` | Compilation     | None    |`function`|
        |                |             | callback        |         |          |
        |                +-------------+-----------------+         |          |
        |                | ``judge``   | Callback after  |         |          |
        |                |             | judging         |         |          |
        +----------------+-------------+-----------------+---------+----------+
        | ``demux``      | ``compile`` | Return `stdout` |``False``| `bool`   |
        |                |             | and `stderr` of |         |          |
        |                |             | compiler        |         |          |
        |                |             | separately      |         |          |
        +----------------+-------------+-----------------+---------+----------+
        | ``iofilename`` | ``in``      | Input filename  | `stdin` | `str`    |
        |                +-------------+-----------------+---------+          |
        |                | ``out``     | Output filename | `stdout`|          |
        +----------------+-------------+-----------------+---------+----------+
        | ``limit``      | ``time``    | Time limit      | ``1``   | `int` or |
        |                |             |                 |         | `float`  |
        +----------------+-------------+-----------------+---------+----------+
        | ``network``                  | Network enabled |``False``| `bool`   |
        +------------------------------+-----------------+---------+----------+
        | ``threads``                  | Thread limit    | None    | `int`    |
        +------------------------------+-----------------+---------+----------+
    :type config: dict
    :param client: Docker client
    :type client: docker.client.DockerClient

    :return: Result
    :rtype: `list`

        === ========== ========================
        Key Value type Description
        === ========== ========================
        `0` `list`     Result of each test case
        `1` `byte`     Compiler output
        === ========== ========================

        Tese case

        === =================================== =====================
        Key Value type                          Description
        === =================================== =====================
        `0` :class:`~dockerjudge.status.Status` Status code
        `1` `tuple`                             `stdout` and `stderr`
        `2` `float`                             Time used
        === =================================== =====================
    """
    config = config or {}
    try:
        processor = getattr(_processor, processor[0])(**processor[1])
    except TypeError:
        try:
            processor = getattr(_processor, processor[0])(*processor[1])
        except TypeError:
            pass
    container = client.containers.run(
        processor.image, detach=True, tty=True,
        network_disabled=not config.get('network')
    )
    try:
        return run(container, processor, source, tests, config)
    finally:
        container.remove(force=True)


def compile_source_code(container, processor, source, config):
    'Compile the source file'
    container.exec_run(f"mkdir -p {processor.workdir}/0")
    put_bin(
        container,
        PurePosixPath(f'{processor.workdir}/0/{processor.source}'),
        source
    )

    exec_run(container, processor.before_compile, f'{processor.workdir}/0')
    exec_result = container.exec_run(processor.compile,
                                     workdir=f'{processor.workdir}/0',
                                     demux=config['demux'].get('compile',
                                                               False))
    if 'compile' in config['callback']:
        config['callback']['compile'](exec_result.exit_code,
                                      exec_result.output)
    exec_run(container, processor.after_compile, f'{processor.workdir}/0')
    return exec_result


def judge_test_cases(container, processor, tests, config):
    'Judge test cases'
    with ThreadPoolExecutor(max_workers=config.get('threads')) as executor:
        futures = []
        for i, test in zip(range(len(tests)), tests):
            futures.append(
                executor.submit(test_case.__init__,
                                container, processor, i + 1, test, config)
            )
            futures[-1].add_done_callback(done_callback(i, config))
    return [
        future.result()
        if not future.exception() else (Status.UE, (None, None), .0)
        for future in futures
    ]


def done_callback(i, config):
    'Return the callback func for concurrent.futures.Future.add_done_callback'
    def _done_callback(future):
        result = ((Status.UE, (None, None), .0)
                  if future.exception() else future.result())
        try:
            config['callback'].get('judge')(i, *result)
        except TypeError:
            pass
    return _done_callback


def run(container, processor, source, tests, config=None):
    'Compile and judge'
    config.setdefault('callback', {})
    config.setdefault('demux', {})
    config.setdefault('iofilename', {})
    exec_result = compile_source_code(container, processor, source, config)
    if exec_result.exit_code:
        return [[(Status.CE, (None, None), .0)] * len(tests),
                exec_result.output]

    res = judge_test_cases(container, processor, tests, config)
    return [res, exec_result.output]
