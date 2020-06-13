'Test case operations'

from pathlib import PurePosixPath
import re
import shlex

from docker.errors import NotFound

from .dockerpy import exec_run, get_bin, put_bin
from .status import Status


def __init__(container, processor, i, ioput, config):
    'Copy binary files to `i` and judge'
    container.exec_run(f'cp -r 0 {i}', workdir=str(processor.workdir))
    exec_run(container, processor.before_judge, f'{processor.workdir}/{i}')
    res = judge(container, processor, i, ioput, config)
    exec_run(container, processor.after_judge, f'{processor.workdir}/{i}')
    return res


def judge(container, processor, i, ioput, config):
    'Judge one of the test cases'
    put_bin(
        container,
        PurePosixPath(
            f"{processor.workdir}/{i}/{config['iofilename']['in']}"
            if 'in' in config.get('iofilename', {})
            else f'{processor.workdir}/{i}.in'
        ),
        ioput[0]
    )
    res = container.exec_run(
        'bash -c ' + shlex.quote(
            "TIMEFORMAT=$'\\n%3lR' && time timeout -sKILL "
            + str(config.get('limit', {}).get('time', 1))
            + ' sh -c ' + shlex.quote(processor.judge)
            + ' > ' + f'{processor.workdir}/{i}.out'
            + (' < ' + f'{processor.workdir}/{i}.in'
               if 'in' not in config.get('iofilename', {}) else '')
        ),
        workdir=f'{processor.workdir}/{i}', demux=True
    )
    duration = re.search('\n([0-9]+)m([0-9]+\\.[0-9]{3})s\n$',
                         res.output[1].decode())
    stderr = res.output[1][:duration.span()[0]]
    duration = int(duration.group(1)) * 60 + float(duration.group(2))
    if res.exit_code == 137:
        return Status.TLE, stderr, duration
    if res.exit_code:
        return Status.RE, stderr, duration
    try:
        output = get_bin(
            container,
            PurePosixPath(
                f"{processor.workdir}/{i}/{config['iofilename']['out']}"
                if 'out' in config.get('iofilename', {})
                else f'{processor.workdir}/{i}.out'
            )
        )
    except NotFound:
        return Status.ONF, stderr, duration
    if output.rstrip() == ioput[1].rstrip():
        return Status.AC, stderr, duration
    return Status.WA, stderr, duration
