'dockerjudge - A Docker Based Online Judge Engine'

import math
from pprint import pprint
import re
import shlex
import sys
import threading

import docker
import ruamel.yaml

__version__ = '0.8.1'


class Thread(threading.Thread):
    'Subclass of threading.Thread with return value'

    def __init__(self, callback, *args, **kwargs):
        self.return_value = ('UE', .0)  # Unknown Error
        self._callback = callback
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            self.return_value = self._target(*self._args, **self._kwargs)
        finally:
            try:
                self._callback(self._args[0], *self.return_value)
            except Exception:
                pass
            del self._target, self._args, self._kwargs, self._callback


def _judge(dir, container, commands, ioput, timeout, iofile) -> (str, float):
    'Run each test case'
    container.exec_run(['bash', '-c', 'mkdir {}'.format(dir)])
    if commands[0]:
        container.exec_run(['bash', '-c',
                            'cd {}&&{}'.format(dir, commands[0].format('..'))])
    if iofile[0]:
        container.exec_run(['bash', '-c', 'echo {}>'
                            '{}/{}'.format(shlex.quote(ioput[0]),
                                           dir, iofile[0])])
        result = container.exec_run(['bash', '-c', 'cd {}&&time timeout -s '
                                     'KILL {} sh -c {}<{}'.format(dir, timeout,
                                                                  shlex.quote(
                                                                      commands
                                                                      [1]
                                                                      % '..'
                                                                  ),
                                                                  iofile[0])],
                                    demux=True)
    else:
        result = container.exec_run(['bash', '-c', 'cd {}&&time echo {}|'
                                     'timeout -s KILL {} '
                                     '{}'.format(dir, shlex.quote(ioput[0]),
                                                 timeout, commands[1] % '..')],
                                    demux=True)
    if commands[2]:
        container.exec_run(['bash', '-c',
                            'cd {}&&{}'.format(dir, commands[2].format('..'))])
    duration = re.search('real\t([0-9]+)m([0-9]+\\.[0-9]{3})s\n'
                         'user\t[0-9]+m[0-9]+\\.[0-9]{3}s\n'
                         'sys\t[0-9]+m[0-9]+\\.[0-9]{3}s\n$',
                         result.output[1].decode())
    duration = int(duration.group(1)) * 60 + float(duration.group(2))
    if result.exit_code == 137:
        return ('TLE', duration)  # Time Limit Exceeded
    if result.exit_code:
        return ('RE', duration)  # Runtime Error
    if iofile[1]:
        cat = container.exec_run(['bash', '-c',
                                  'cat {}/{}'.format(dir, iofile[1])],
                                 demux=True)
        if cat.exit_code:
            return ('ONF', duration)  # Output Not Found
        output = cat.output[0]
    else:
        output = result.output[0]
    if (output or b'').decode().rstrip() != ioput[1].rstrip():
        return ('WA', duration)  # Wrong Answer
    return ('AC', duration)  # Accepted


def judge(settings, source='', tests=[], timeout=1, iofile=(None, None),
          callback={}, split=0, client=docker.from_env()):
    'Main judge function'
    tests = list(tests)
    if not split:
        split = len(tests)
    container = client.containers.run(settings['image'], detach=True,
                                      network_disabled=True, tty=True)
    try:
        container.exec_run(['bash', '-c', 'echo {} > {}'.format(
            shlex.quote(source), settings['source'])])
        compiler = container.exec_run(settings['compile'], demux=True)
        if callback.get('compiling'):
            callback['compiling'](compiler.exit_code,
                                  (compiler.output[1] or b'').decode())
        if compiler.exit_code:
            result = [('CE', .0) for test in tests]
        else:
            result = []
            for i in range(math.ceil(len(tests) / split)):
                threads = []
                for j in range(i * split, min((i + 1) * split, len(tests))):
                    thread = Thread(target=_judge,
                                    args=(j, container,
                                          (settings.get('before_judging'),
                                           settings['judge'],
                                           settings.get('after_judging')),
                                          tests[j], timeout, iofile),
                                    callback=callback.get('judging'))
                    thread.start()
                    threads.append(thread)
                for thread in threads:
                    thread.join()
                    result.append(thread.return_value)
        return [result, (compiler.output[1] or b'').decode()]
    finally:
        container.remove(force=True)


if __name__ == '__main__':
    pprint(judge(ruamel.yaml.YAML().load(open('settings.yaml'))
                 [sys.argv[1]][sys.argv[2]],
                 sys.stdin.read(), zip(sys.argv[3::2], sys.argv[4::2])))
