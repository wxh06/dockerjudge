'dockerjudge - A Docker Based Online Judge Engine'

from pprint import pprint
import re
import shlex
import sys
import threading

import docker
import ruamel.yaml

__version__ = '0.4'


class Thread(threading.Thread):
    'Subclass of threading.Thread with return value'
    return_value = 'UE'  # Unknown Error

    def run(self):
        try:
            if self._target:
                self.return_value = self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs


def _judge(container, commands, stdio, timeout=1):
    'Run each test case'
    if commands[0]:
        container.exec_run(commands[0])
    result = container.exec_run(['bash', '-c', 'time echo {}|timeout -s KILL '
                                 '{} {}'.format(shlex.quote(stdio[0]), timeout,
                                                commands[1])], demux=True)
    duration = re.search('real\t([0-9]+)m([0-9]+\\.[0-9]{3})s\n'
                         'user\t[0-9]+m[0-9]+\\.[0-9]{3}s\n'
                         'sys\t[0-9]+m[0-9]+\\.[0-9]{3}s\n$',
                         result.output[1].decode())
    duration = int(duration.group(1)) * 60 + float(duration.group(2))
    if commands[2]:
        container.exec_run(commands[2])
    if result.exit_code == 137:
        return ('TLE', duration)  # Time Limit Exceeded
    if result.exit_code:
        return ('RE', duration)  # Runtime Error
    if (result.output[0] or b'').decode().rstrip() != stdio[1].rstrip():
        return ('WA', duration)  # Wrong Answer
    return ('AC', duration)  # Accepted


def judge(settings, source='', tests=(), timeout=1, client=docker.from_env()):
    'Main judge function'
    container = client.containers.run(settings['image'], detach=True,
                                      network_disabled=True, tty=True)
    try:
        container.exec_run(['bash', '-c', 'echo {} > {}'.format(
            shlex.quote(source), settings['source'])])
        if 'before_compile' in settings:
            container.exec_run(settings['before_compile'])
        compiler = container.exec_run(settings['compile'], demux=True)
        if 'before_compile' in settings:
            container.exec_run(settings['after_compile'])
        if compiler.exit_code:
            result = [('CE', .0) for test in tests]
        else:
            threads = []
            for stdin, stdout in tests:
                thread = Thread(target=_judge,
                                args=(container, (settings.get('before_judge'),
                                                  settings['judge'],
                                                  settings.get('after_judge')),
                                      (stdin, stdout), timeout))
                thread.start()
                threads.append(thread)
            result = []
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
