'dockerjudge - A Docker Based Online Judge Engine'

from math import ceil
from pathlib import PurePosixPath

import docker

from .dockerpy import exec_run, put_bin
from .status import Status
from . import test_case
from .thread import Thread

__version__ = '1.2.3'


def judge(processor, source, tests, config=None,
          client=docker.from_env()):
    'Main function'
    config = config or {}
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
                                     workdir=f'{processor.workdir}/0')
    if 'compile' in config['callback']:
        config['callback']['compile'](exec_result.exit_code,
                                      exec_result.output)
    exec_run(container, processor.after_compile, f'{processor.workdir}/0')
    return exec_result


def judge_test_cases(container, processor, tests, config):
    'Judge test cases'
    res = []
    for i in range(ceil(len(tests) / config.setdefault('threads',
                                                       len(tests)))):
        threads = []
        for j in range(i * config['threads'],
                       min((i + 1) * config['threads'], len(tests))):
            threads.append(
                Thread(
                    target=test_case.__init__,
                    args=(container, processor, j + 1, tests[j], config),
                    callback=config['callback'].get('judge')
                )
            )
            threads[-1].start()
        for thread in threads:
            thread.join()
            res.append(thread.return_value)
    return res


def run(container, processor, source, tests, config=None):
    'Compile and judge'
    config.setdefault('callback', {})
    exec_result = compile_source_code(container, processor, source, config)
    if exec_result.exit_code:
        return [[(Status.CE, (None, None), .0)] * len(tests),
                exec_result.output]

    res = judge_test_cases(container, processor, tests, config)
    return [res, exec_result.output]
