import codecs
import os.path
import re

import setuptools


def read(path):
    with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     path)) as fp:
        return fp.read()


def get_version(file_path):
    versions = re.findall(r"^__version__ = ['\"]([^'\"]*)['\"]",
                          read(file_path), re.M)
    if versions:
        return versions[-1]
    raise RuntimeError('Unable to find version string.')


setuptools.setup(
    name='dockerjudge',
    version=get_version('dockerjudge/__init__.py'),
    author='汪心禾',
    author_email='wangxinhe06@gmail.com',
    description='A Docker Based Online Judge Engine',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/wangxinhe2006/dockerjudge',
    packages=['dockerjudge'],
    install_requires=[
        'docker[tls]>=3.7',
        'ruamel.yaml'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)
