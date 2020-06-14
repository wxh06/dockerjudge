'Extentions of Docker SDK for Python'

import io
import shlex
import tarfile


def tar_bin(filename, data):
    'Write the binary file `filename` into a tarfile'
    bytes_io = io.BytesIO()
    tar = tarfile.open(mode='w', fileobj=bytes_io)
    tarinfo = tarfile.TarInfo(filename)
    tarinfo.size = len(data)
    tar.addfile(tarinfo, io.BytesIO(data))
    tar.close()
    bytes_io.seek(0)
    return bytes_io.read()


def put_bin(container, path, data):
    'Extends docker.models.containers.Container.put_archive'
    return container.put_archive(path.parent, tar_bin(path.name, data))


def get_bin(container, path):
    'Extends docker.models.containers.Container.get_archive'
    bytes_io = io.BytesIO()
    for chunk in container.get_archive(path)[0]:
        bytes_io.write(chunk)
    bytes_io.seek(0)
    tar = tarfile.open(mode='r', fileobj=bytes_io)
    return tar.extractfile(path.name).read()


def exec_run(container, command, workdir):
    'Extends docker.models.containers.Container.exec_run'
    if command:
        return container.exec_run(f'sh -c {shlex.quote(command)}'
                                  if isinstance(command, str) else command,
                                  workdir=workdir)
    return None
