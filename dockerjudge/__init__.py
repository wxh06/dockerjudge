'dockerjudge - A Docker Based Online Judge Engine'

import shlex
import sys
import threading

import docker
import ruamel.yaml


class Thread(threading.Thread):
    'Subclass of threading.Thread with return value'
    return_value = None
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
    result = container.exec_run(['sh', '-c', 'echo ' + shlex.quote(stdio[0]) + ' | timeout -k '
                                 + (str(timeout) + ' ') * 2 + commands[1]], demux=True)
    if commands[2]:
        container.exec_run(commands[2])
    if result.exit_code == 124:
        return 'TLE'
    if result.exit_code:
        return 'RE'
    if result.output[0].decode().rstrip() != stdio[1].rstrip():
        return 'WA'
    return 'AC'

def judge(settings, source='', tests=(), timeout=1, client=docker.from_env()):
    'Main judge function'
    container = client.containers.run(settings['image'], detach=True,
                                      network_disabled=True, tty=True)
    try:
        container.exec_run(['sh', '-c', 'echo ' + shlex.quote(source) + ' > ' + settings['source']])
        if 'before_compile' in settings:
            container.exec_run(settings['before_compile'])
        compiler = container.exec_run(settings['compile'], demux=True)
        if 'before_compile' in settings:
            container.exec_run(settings['after_compile'])
        if not compiler.exit_code:
            threads = []
            for stdin, stdout in tests:
                threads.append(Thread(target=_judge,
                                      args=(container, (settings.get('before_judge'),
                                                        settings['judge'],
                                                        settings.get('after_judge')),
                                            (stdin, stdout), timeout)))
                threads[-1].start()
            result = []
            for thread in threads:
                thread.join()
                result.append(thread.return_value)
            return [result, (compiler.output[1] or b'').decode()]
        return [['CE' for test in tests], compiler.output[1].decode()]
    finally:
        container.remove(force=True)

if __name__ == '__main__':
    print(judge(ruamel.yaml.YAML().load(open('settings.yaml'))[sys.argv[1]][sys.argv[2]],
                sys.stdin.read(), zip(sys.argv[3::2], sys.argv[4::2])))
