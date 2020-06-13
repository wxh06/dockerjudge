'dockerjudge - A Docker Based Online Judge Engine'

from pathlib import PurePosixPath

import docker

from .dockerpy import exec_run, put_bin
from .status import Status
from . import test_case

__version__ = '1.0.0'


def judge(processor, source, tests, config=None,
          client=docker.from_env()):
    'Main function'
    config = config or {}
    container = client.containers.run(processor.image, detach=True,
                                      network_disabled=True, tty=True)
    try:
        return run(container, processor, source, tests, config)
    finally:
        container.remove(force=True)


def run(container, processor, source, tests, config):
    'Compile and judge'
    container.exec_run(f"mkdir -p {processor.workdir}/0")
    put_bin(
        container,
        PurePosixPath(f'{processor.workdir}/0/{processor.source}'),
        source
    )

    exec_run(container, processor.before_compile, f'{processor.workdir}/0')
    exec_result = container.exec_run(processor.compile,
                                     workdir=f'{processor.workdir}/0')
    if exec_result.exit_code:
        return [[[Status.CE, exec_result.output, .0]] * len(tests),
                exec_result.output]
    exec_run(container, processor.after_compile, f'{processor.workdir}/0')

    res = []
    for i, test in zip(range(1, len(tests) + 1), tests):
        res.append(test_case.__init__(container, processor, i, test, config))
    return [res, exec_result.output]
