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


def _get_io_file_path(ioro, processor, i, config):
    'Get the absolute path of input or output file'
    return PurePosixPath(
        f"{processor.workdir}/{i}/{config['iofilename'][ioro]}"
        if config['iofilename'].get(ioro)
        else f'{processor.workdir}/{i}.{ioro}'
    )


def judge(container, processor, i, ioput, config):
    'Judge one of the test cases'
    put_bin(container, _get_io_file_path('in', processor, i, config), ioput[0])
    res = container.exec_run(
        'bash -c ' + shlex.quote(
            "TIMEFORMAT=$'\\n%3lR' && time timeout -sKILL "
            + str(config.get('limit', {}).get('time', 1))
            + ' sh -c ' + shlex.quote(processor.judge)
            + ' > ' + f'{processor.workdir}/{i}.out'
            + (' < ' + f'{processor.workdir}/{i}.in'
               if not config['iofilename'].get('in') else '')
        ),
        workdir=f'{processor.workdir}/{i}', demux=True
    )
    duration = re.search('\n([0-9]+)m([0-9]+\\.[0-9]{3})s\n$',
                         res.output[1].decode())
    stderr = res.output[1][:duration.span()[0]]
    duration = int(duration.group(1)) * 60 + float(duration.group(2))
    if res.exit_code == 137:
        return Status.TLE, (None, stderr), duration
    if res.exit_code:
        return Status.RE, (None, stderr), duration
    try:
        output = get_bin(container,
                         _get_io_file_path('out', processor, i, config))
    except NotFound:
        return Status.ONF, (None, stderr), duration
    return (Status.AC if output.rstrip() == ioput[1].rstrip() else Status.WA,
            (output, stderr), duration)
