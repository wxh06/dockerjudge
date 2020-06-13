'Processors'
# pylint: disable = missing-function-docstring, too-few-public-methods

from enum import Enum
from pathlib import PurePosixPath


class Processor():
    'Defines the operations of a multi-version programming language processor'

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

    def __init__(self, language=None, version=None,
                 filenames: {'src': r'a.(c|cpp)',
                             'bin': 'a.out'} = None,  # pylint: disable = C0326
                 options=None):
        lang = (language if isinstance(language, self.Language)
                else self.Language[language] if language in ['c', 'cpp']
                else self.Language(language) if language in ['C', 'C++']
                else self.Language.cpp)
        fns = filenames or {}
        args = options or []

        self.image = 'gcc' + (f':{version}' if version else '')
        self.source = fns.get('src', f'a.{lang.name}')
        self.compile = ([{self.Language.c: 'gcc',
                          self.Language.cpp: 'g++'}[lang],
                         self.source]
                        + (['-o', fns['bin']]
                           if fns.get('bin') else []) + args)
        self.after_compile = ['rm', self.source]
        # self.before_judge = 'ls'
        self.judge = f"./{fns.get('bin', 'a.out')}"
