'Processors'
# pylint: disable = missing-function-docstring, too-few-public-methods

from enum import Enum
from pathlib import PurePosixPath


class Processor():
    'Defines the operations of a multi-version programming language processor'

    @staticmethod
    def _get_image_with_tag(image, tag):
        return image + (f':{tag}' if tag else '')

    image = None
    workdir = PurePosixPath('/dockerjudge')
    source = None
    before_compile = None
    compile = None
    after_compile = None
    before_judge = None
    judge = None
    after_judge = None


class GCC(Processor):
    'GNU project C and C++ compiler'

    class Language(Enum):
        'C or C++'
        c = 'C'
        cpp = 'C++'

    def _get_language(self, language):
        if isinstance(language, self.Language):
            return language
        return (self.Language[language] if language in ['c', 'cpp']
                else self.Language(language) if language in ['C', 'C++']
                else self.Language.cpp)

    def __init__(self, language=None, version=None,
                 filenames=None, options=None):
        lang = self._get_language(language)
        fns = filenames or {}
        args = options or []

        self.image = self._get_image_with_tag('gcc', version)
        self.source = fns.get('src', f'a.{lang.name}')
        self.compile = ([{self.Language.c: 'gcc',
                          self.Language.cpp: 'g++'}[lang],
                         self.source]
                        + (['-o', fns['bin']]
                           if fns.get('bin') else []) + args)
        self.after_compile = ['rm', self.source]
        self.judge = f"./{fns.get('bin', 'a.out')}"


class Python(Processor):
    'CPython'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('python', version)
        self.source = '__init__.py'
        self.compile = ['python', '-m', 'compileall', '.']
        self.judge = f'python {self.source}'


class Go(Processor):
    'The Go Programming Language'

    def __init__(self, version=None, filenames=None, options=None):
        fns = filenames or {}
        args = options or []

        self.image = self._get_image_with_tag('golang', version)
        self.source = fns.get('src', 'main.go')
        self.compile = (['go', 'build']
                        + (['-o', fns['bin']]
                           if fns.get('bin') else []) + args
                        + [self.source])
        self.after_compile = ['rm', self.source]
        self.judge = f"./{fns.get('bin', 'main')}"


class OpenJDK(Processor):
    'Open Java Development Kit'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('openjdk', version)
        self.source = 'Main.java'
        self.compile = ['javac', self.source]
        self.after_compile = ['rm', self.source]
        self.judge = 'java Main'


class Node(Processor):
    'Node.js®'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('node', version)
        self.source = 'index.js'
        self.compile = ['node', '-c', self.source]
        self.judge = f'node {self.source}'
