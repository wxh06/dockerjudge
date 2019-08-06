import setuptools

from dockerjudge import __version__


setuptools.setup(
    name='dockerjudge',
    version=__version__,
    author='汪心禾',
    author_email='wangxinhe06@gmail.com',
    description='A Docker Based Online Judge Engine',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wangxinhe2006/dockerjudge',
    packages=['dockerjudge'],
    install_requires=[
        'docker[tls]>=3.7',
        'ruamel.yaml'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
    ],
)
