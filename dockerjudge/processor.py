'Processors'
# pylint: disable = missing-function-docstring, too-few-public-methods

from enum import Enum
from pathlib import PurePosixPath
import shlex


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


class _Language(Enum):
    'Get programming language from enum'

    @classmethod
    def __get_language(cls, language, default=None):
        if isinstance(language, cls):
            return language
        try:
            return cls[language]
        except KeyError:
            try:
                return cls(language)
            except ValueError:
                return cls.__get_language(default)


class Bash(Processor):
    "Bash is the GNU Project's Bourne Again SHell"

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('bash', version)
        self.source = 'bash.sh'
        self.compile = ['bash', '-n', self.source]
        self.judge = f'bash {self.source}'


class Clang(Processor):
    'Clang C Language Family Frontend for LLVM'

    class Language(_Language):
        'Programming language, C (c) or C++ (cpp)'
        c = 'C'
        cpp = 'C++'

        @classmethod
        def _get_language(cls, language):
            return super().__get_language(language, cls.cpp)

    def __init__(self, language=None, version=None,
                 filenames=None, options=None):
        lang = self.Language._get_language(language)
        fns = filenames or {}
        args = options or []

        self.image = 'clangbuiltlinux/ubuntu' + f':llvm{version}-latest'
        self.source = fns.get('src', f'a.{lang.name}')
        self.compile = ([{self.Language.c: 'clang',
                          self.Language.cpp: 'clang++'}[lang] + f'-{version}',
                         self.source]
                        + (['-o', fns['bin']] if fns.get('bin')
                           else [])
                        + (shlex.split(args) if isinstance(args, str)
                           else args))
        self.after_compile = ['rm', self.source]
        self.judge = f"./{fns.get('bin', 'a.out')}"


class GCC(Processor):
    'GNU project C, C++ and Go compiler'

    class Language(_Language):
        'Programming language, C, C++ or Go'
        c = 'C'
        cpp = 'C++'
        go = 'Go'

        @classmethod
        def _get_language(cls, language):
            return super().__get_language(language, cls.cpp)

    def __init__(self, language=None, version=None,
                 filenames=None, options=None):
        lang = self.Language._get_language(language)
        fns = filenames or {}
        args = options or []

        self.image = self._get_image_with_tag('gcc', version)
        self.source = fns.get('src', f'a.{lang.name}')
        self.compile = ([{self.Language.c: 'gcc',
                          self.Language.cpp: 'g++',
                          self.Language.go: 'gccgo'}[lang],
                         self.source]
                        + (['-o', fns['bin']] if fns.get('bin')
                           else [])
                        + (shlex.split(args) if isinstance(args, str)
                           else args))
        self.after_compile = ['rm', self.source]
        self.judge = f"./{fns.get('bin', 'a.out')}"


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


class Mono(Processor):
    'Mono'

    class Language(_Language):
        'Programming language, C# or Visual Basic'
        vb = 'Visual Basic'
        csharp = 'C#'

        @classmethod
        def _get_language(cls, language):
            return super().__get_language(language, cls.csharp)

    def __init__(self, language=None, version=None):
        lang = self.Language._get_language(language)

        self.image = self._get_image_with_tag('mono', version)
        self.source = f'''mono.{
            {self.Language.csharp: 'cs', self.Language.vb: 'vb'}[lang]
        }'''
        self.compile = [{self.Language.csharp: 'csc',
                         self.Language.vb: 'vbnc'}[lang],
                        self.source]
        self.after_compile = ['rm', self.source]
        self.judge = 'mono mono.exe'


class Node(Processor):
    'Node.js®'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('node', version)
        self.source = 'index.js'
        self.compile = ['node', '-c', self.source]
        self.judge = f'node {self.source}'


class OpenJDK(Processor):
    'Open Java Development Kit'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('openjdk', version)
        self.source = 'Main.java'
        self.compile = ['javac', self.source]
        self.after_compile = ['rm', self.source]
        self.judge = 'java Main'


class PHP(Processor):
    'PHP'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('php', version)
        self.source = 'index.php'
        self.compile = ['php', '-l', self.source]
        self.judge = f'php {self.source}'


class PyPy(Processor):
    'PyPy'

    def __init__(self, version=None):
        pypy = 'pypy' if str(version).startswith('2') else 'pypy3'

        self.image = self._get_image_with_tag('pypy', version)
        self.source = '__init__.py'
        self.compile = [pypy, '-m', 'compileall', '.']
        self.judge = f'{pypy} {self.source}'


class Python(Processor):
    'CPython'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('python', version)
        self.source = '__init__.py'
        self.compile = ['python', '-m', 'compileall', '.']
        self.judge = f'python {self.source}'


class Ruby(Processor):
    'Ruby'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('ruby', version)
        self.source = 'ruby.rb'
        self.compile = ['ruby', '-wc', self.source]
        self.judge = f'ruby {self.source}'


class Swift(Processor):
    'Swift'

    def __init__(self, version=None):
        self.image = self._get_image_with_tag('swift', version)
        self.source = 'main.swift'
        self.compile = ['swiftc', self.source]
        self.judge = './main'
