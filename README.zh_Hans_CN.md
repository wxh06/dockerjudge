<p align="center">
  <a href="https://github.com/piterator-org">
    <img src="https://static.piterator.com/piterator/logo.svg" alt="Piterator" width="20%">
    <br>
    由 <strong>Piterator</strong> 团队用 &lt;3 制作
  </a>
</p>

# dockerjudge
[![Maintainability](https://api.codeclimate.com/v1/badges/dfe666a2140cd3390e56/maintainability)](https://codeclimate.com/github/wxh06/dockerjudge/maintainability)
[![Python 包](https://github.com/wxh06/dockerjudge/workflows/Python%20package/badge.svg)](https://github.com/wxh06/dockerjudge/actions?query=workflow%3A%22Python+package%22)
[![上传 Python 包](https://github.com/wxh06/dockerjudge/workflows/Upload%20Python%20Package/badge.svg)](https://github.com/wxh06/dockerjudge/actions?query=workflow%3A%22Upload+Python+Package%22)
[![构建状态](https://travis-ci.com/wxh06/dockerjudge.svg)](https://travis-ci.com/wxh06/dockerjudge)
[![CodeCov](https://codecov.io/gh/wxh06/dockerjudge/graph/badge.svg)](https://codecov.io/gh/wxh06/dockerjudge)
[![Python 版本](https://img.shields.io/pypi/pyversions/dockerjudge.svg)](https://www.python.org/downloads/)
[![GitHub pre-release](https://img.shields.io/github/release-pre/wxh06/dockerjudge.svg)](https://github.com/wxh06/dockerjudge/releases)
[![PyPI](https://img.shields.io/pypi/v/dockerjudge.svg)](https://pypi.org/project/dockerjudge/#history)
[![Wheel](https://img.shields.io/pypi/wheel/dockerjudge.svg)](https://pypi.org/project/dockerjudge/#files)
[![License](https://img.shields.io/github/license/wxh06/dockerjudge.svg)](LICENSE)

🎌 [🇺🇸 English](README.md) | **🇨🇳 大陆简体**

**基于 [Docker](https://www.docker.com/) 的在线测评引擎**，支持 10+ 个编程语言处理程序：
- [Shell](https://zh.wikipedia.org/zh-cn/Unix_shell)
  - [Bash (**B**ourne-**A**gain **sh**ell)](https://zh.wikipedia.org/zh-cn/Bash)
- [C](https://zh.wikipedia.org/zh-cn/C语言)/[C++](https://zh.wikipedia.org/zh-cn/C%2B%2B)
  - [GCC (The **G**NU **C**ompiler **C**ollection)](https://gcc.gnu.org/)
  - [LLVM Clang](https://clang.llvm.org/)
- [.NET](https://docs.microsoft.com/zh-cn/dotnet/) ([C#](https://docs.microsoft.com/zh-cn/dotnet/csharp/) & [Visual Basic](https://docs.microsoft.com/zh-cn/dotnet/visual-basic/))
  - [Mono](https://www.mono-project.com/)
- [Go](https://golang.google.cn/)
  - [`go`](https://golang.google.cn/dl/)
  - [`gccgo` (GCC)](https://golang.google.cn/doc/install/gccgo)
- [Java](https://www.oracle.com/cn/java/)
  - [OpenJDK](https://openjdk.java.net/)
- [Node.js](https://nodejs.org/zh-cn/)
  - [`node`](https://nodejs.org/zh-cn/download/)
- [PHP](https://www.php.net/)
  - [`php`](https://www.php.net/downloads)
- [Python](https://www.python.org/)
  - [CPython](https://www.python.org/downloads/)
  - [PyPy](https://www.pypy.org/)
- [Ruby](https://www.ruby-lang.org/zh_cn/)
  - [`ruby`](https://www.ruby-lang.org/zh_cn/downloads/)
- [Swift](https://swift.org/)
  - [`swiftc`](https://swift.org/swift-compiler/)


## 安装
### 从 [Python 包索引 (PyPI)](https://pypi.org/)
[dockerjudge · PyPI](https://pypi.org/project/dockerjudge/)
- [PyPI](https://pypi.org/simple/dockerjudge/)
- [阿里巴巴开源镜像站](https://mirrors.aliyun.com/pypi/simple/dockerjudge/)
- [清华大学开源软件镜像站 | Tsinghua Open Source Mirror](https://pypi.tuna.tsinghua.edu.cn/simple/dockerjudge/)

#### 通过 [pip](https://pip.pypa.io/)
```sh
pip install dockerjudge
```

#### 通过 [Easy install](https://setuptools.readthedocs.io/en/latest/easy_install.html) (不建议)
```sh
easy_install dockerjudge
```

### 从 [GitHub](https://github.com/)
[wxh06/dockerjudge: A Docker Based Online Judge Engine](https://github.com/wxh06/dockerjudge)
- HTTPS: `https://github.com/wxh06/dockerjudge.git`
- SSH: `git@github.com:wxh06/dockerjudge.git`
```sh
git clone https://github.com/wxh06/dockerjudge.git
cd dockerjudge

make pip && make  # python3 -m pip install -Ur requirements.txt && python3 setup.py build
sudo make install  # python3 setup.py install
```


## 用法示例
```python
>>> from dockerjudge import judge
>>> from dockerjudge.processor import GCC, Clang, Bash, Python, Node, OpenJDK, PHP, Ruby, Mono, Swift
>>>
>>> judge(
...     GCC(GCC.Language.c),  # 或 `GCC('c')` / `GCC('C')`，意为用 `gcc` 命令编译 C 语言源码
...     b'''
...         #include <stdio.h>
...         int main() {
...             int a, b;
...             scanf("%d %d", &a, &b);
...             printf("%d", a / b);
...             return 0;
...         }
...     ''',
...     [
...         (b'1 1', b'1'),  # AC
...         (b'1 2', b'0.5'),  # WA
...         (b'0 0', b'')  # RE
...     ]
... )
[
    [
        (<Status.AC: 'Accepted'>, (b'1', b''), 0.001),
        (<Status.WA: 'Wrong Answer'>, (b'0', b''), 0.001),
        (<Status.RE: 'Runtime Error'>, (None, b'Floating point exception (core dumped)\n'), 0.01)
    ],
    b''
]
>>>
>>> judge(GCC(GCC.Language.c), b'', [(b'', b'')])  # CE
[
    [
        (<Status.CE: 'Compilation Error'>, (None, None), 0.0)
    ],
    b"/usr/bin/ld: /usr/lib/x86_64-linux-gnu/crt1.o: in function `_start':\n(.text+0x20): undefined reference to `main'\ncollect2: error: ld returned 1 exit status\n"
]
>>>
>>> judge(
...     GCC(GCC.Language.cpp),  # 或 `GCC('cpp')` / `GCC('C++')`，意为用 `g++` 命令编译 C++ 源码
...     b'''
...         #include <cstdio>
...         int main() {
...             printf("Hello, world!");
...             while (true)
...                 ;
...         }
...     ''',
...     [
...         (b'', b'Hello, world!')  # TLE
...     ],
...     {
...         'limit': {
...             'time': .1
...         }
...     }
... )
[
    [
        (<Status.TLE: 'Time Limit Exceeded'>, (None, b'bash: line 1:    35 Killed                  timeout -sKILL 0.1 sh -c ./a.out > /dockerjudge/1.out < /dockerjudge/1.in\n'), 0.100)
    ],
    b''
]
>>>
>>> judge(
...     GCC(
...         GCC.Language.c,
...         'latest',  # GCC 版本号，比如 `4` 或 `4.8` 等
...         {'bin': 'a'}  # `gcc` 之 `-o` 选项的实参——二进制文件名
...     ),
...     b'''
...         #include <stdio.h>
...         int main() {
...             int a, b;
...             freopen("a.in", "r", stdin);  // Open `a.in` as stdin
...             scanf("%d %d", &a, &b);  // Scan from `a.in`
...             freopen("a.out", "w", stdout);  // Open `a.out` as stdout
...             printf("%d", a / b);  // Print to `a.out`
...             return 0;
...         }
...     ''',
...     [
...         (b'1 1', b'1'),  # AC
...         (b'1 2', b'0.5'),  # WA
...         (b'0 0', b'')  # RE
...     ],
...     {
...         'iofilename': {
...             'in': 'a.in',
...             'out': 'a.out'
...         }
...     }
... )
[
    [
        (<Status.AC: 'Accepted'>, (b'1', b''), 0.001),
        (<Status.WA: 'Wrong Answer'>, (b'0', b''), 0.001),
        (<Status.RE: 'Runtime Error'>, (None, b'Floating point exception (core dumped)\n'), 0.001)
    ],
    b''
]
>>>
>>> judge(
...     GCC(GCC.Language.c, filenames={'bin': 'a'}),
...     b'''
...         #include <stdio.h>
...         int main() {
...             int a, b;
...             scanf("%d %d", &a, &b);
...             printf("%d", a / b);
...             return 0;
...         }
...     ''',
...     [
...         (b'1 1', b'1'),
...         (b'0 0', b'')
...     ],
...     {
...         'iofilename': {
...             'out': 'a.out'  # ONF
...         }
...     }
... )
[
    [
        (<Status.ONF: 'Output Not Found'>, (None, b''), 0.001),
        (<Status.RE: 'Runtime Error'>, (None, b'Floating point exception (core dumped)\n'), 0.001)
    ],
    b''
]
>>>
>>> judge(  # BTW，从 4.9 开始 GCC 还支持 Go，叫 `gccgo`
...     GCC(GCC.Language.go),
...     b'package main\n'
...     b''
...     b'import "fmt"\n'
...     b''
...     b'func main() {\n'
...     br'    fmt.Printf("hello, world\n")'b'\n'
...     b'}\n',
...     [(b'', b'hello, world')]
... )
[
    [
        (<Status.AC: 'Accepted'>, (b'hello, world\n', b''), 0.02)
    ],
    b''
]
>>>
>>> judge(
...     Clang(  # 除了 GCC，还支持 LLVM Clang（参数与 GCC 相同）
...         Clang.Language.c,  # 仅支持 C 与 C++
...         11  # **必须**提供 LLVM CLang 的版本号！
...     ),
...     b'',  # CE
...     [
...         (b'', b'')
...     ]
... )
[
    [
        (<Status.CE: 'Compilation Error'>, (None, None), 0.0)
    ],
    b"/usr/bin/ld: /usr/bin/../lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu/crt1.o: in function `_start':\n'
    b"(.text+0x24): undefined reference to `main'\n"
    b'clang: error: linker command failed with exit code 1 (use -v to see invocation)\n'
]
>>>
>>> # 亦支持其它编程语言
>>> judge(Bash(), b'echo Hello, world!', [(b'', b'Hello, world!')])  # Bash
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!\n', b''), 0.001)
    ],
    b''
]
>>>
>>> judge(Python(3), b"print('Hello, world!')", [(b'', b'Hello, world!')])  # Python 3
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!\n', b''), 0.05)
    ],
    b"Listing '.'...\n"
    b"Compiling './__init__.py'...\n"
]
>>> judge(PyPy(), b"print('Hello, world!')", [(b'', b'Hello, world!')])  # PyPy 3
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!\n', b''), 0.075)
    ],
    b"Listing '.'...\n"
    b"Compiling './__init__.py'...\n"
]
>>>
>>> judge(Node(12), b'console.log("Hello World")', [(b'', b'Hello World')])  # Node.js
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello World\n', b''), 0.05)
    ],
    b''
]
>>>
>>> judge(  # Java / OpenJDK
...     OpenJDK(), #  默认的源代码文件名是 `Main.java`，即 public class 名称应该为 `Main`
...     b'''
...         public class Main {
...             public static void main(String[] args) {
...                 System.out.println("Hello, world!");
...             }
...         }
...     ''',
...     [
...         (b'', b'Hello, world!')
...     ]
... )
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!\n', b''), 0.1)
    ],
    b''
]
>>>
>>> judge(PHP(), b'<?php echo "Hello, world!";', [(b'', b'Hello, world!')])  # PHP
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!', b''), 0.05)
    ],
    b'No syntax errors detected in index.php\n'
]
>>>
>>> judge(Ruby(), b'print "Hello, world!";', [(b'', b'Hello, world!')])  # Ruby
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!', b''), 0.05)
    ],
    b'Syntax OK\n'
]
>>>
>>> judge(
...     Mono(Mono.Language.csharp),  # C# (Mono)
...     b'''
...         using System;
... 
...         public class HelloWorld
...         {
...             public static void Main(string[] args)
...             {
...                 Console.WriteLine ("Hello Mono World");
...             }
...         }
...     ''',
...     [
...         (b'', b'Hello Mono World')
...     ]
... )
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello Mono World\n', b''), 0.02)
    ],
    b'Microsoft (R) Visual C# Compiler version 3.5.0-beta1-19606-04 (d2bd58c6)\n'
    b'Copyright (C) Microsoft Corporation. All rights reserved.\n'
    b'\n'
]
>>> judge(
...     Mono(Mono.Language.vb),  # Visual Basic (Mono)
...     b'''
...         Imports System
... 
...         Module HelloWorld
...             Sub Main()
...                 Console.WriteLine("Hello World!")
...             End Sub
...         End Module
...     ''',
...     [
...         (b'', b'Hello World!')
...     ]
... )
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello World!\n', b''), 0.024)
    ],
    b'Visual Basic.Net Compiler version 0.0.0.5943 (Mono 4.7 - tarball)\n'
    b'Copyright (C) 2004-2010 Rolf Bjarne Kvinge. All rights reserved.\n'
    b'\n'
    b"Assembly 'mono, Version=0.0, Culture=neutral, PublicKeyToken=null' saved successfully to '/dockerjudge/0/mono.exe'.\r\n"
    b'Compilation successful\r\n'
    b'Compilation took 00:00:00.0000000\n'
]
>>>
>>> judge(Swift(), b'print("Hello, world!")', [(b'', b'Hello, world!')])  # Swift
[
    [
        (<Status.AC: 'Accepted'>, (b'Hello, world!\n', b''), 0.2)
    ],
    b''
]
```


## [许可协议](LICENSE)
以 [**Apache License 2.0**](https://www.apache.org/licenses/LICENSE-2.0) 进行授权
<a href="https://www.apache.org/foundation/press/kit/#wide"><img src="https://www.apache.org/foundation/press/kit/asf_logo_wide.svg" alt="Wide Apache Software Foundation Logo with Feather.svg" height="32" align="right"></a>
