'dockerjudge - A Docker Based Online Judge Engine'

import shlex
import sys
import threading

import docker
import ruamel.yaml


def _judge(container, command, stdin='', stdout='', timeout=1):
    'Run each test case'
    result = container.exec_run(['sh', '-c', 'echo ' + shlex.quote(stdin) + ' | timeout -k '
                                 + (str(timeout) + ' ') * 2 + command], demux=True)
    if result.exit_code == 124:
        raise TimeoutError('TLE')
    if result.exit_code:
        raise Exception('RE')
    assert result.output[0].decode().rstrip() == stdout.rstrip(), 'WA'

def judge(settings, source='', tests=(), timeout=1, client=docker.from_env()):
    'Main judge function'
    container = client.containers.run(settings['image'], detach=True,
                                      network_disabled=True, tty=True)
    try:
        container.exec_run(['sh', '-c', 'echo ' + shlex.quote(source) + ' > ' + settings['source']])
        result = container.exec_run(settings['compile'], demux=True)
        if not result.exit_code:
            threads = []
            for stdin, stdout in tests:
                threads.append(threading.Thread(target=_judge, args=(container, settings['judge'],
                                                                     stdin, stdout, timeout)))
                threads[-1].start()
            for thread in threads:
                thread.join()
        else:
            print(result.output[1].decode().rstrip())
    finally:
        container.remove(force=True)

if __name__ == '__main__':
    judge(ruamel.yaml.YAML().load(open('settings.yaml'))[sys.argv[1]][sys.argv[2]],
          sys.stdin.read(), zip(sys.argv[3::2], sys.argv[4::2]))
