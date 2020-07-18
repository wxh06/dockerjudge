'Test dockerjudge'
# pylint: disable = C0103, C0115, C0116

from time import time
import unittest

from dockerjudge import judge
from dockerjudge.processor import (Bash, Clang, GCC, Go, Mono, Node, OpenJDK,
                                   PHP, PyPy, Python, Ruby, Swift)
from dockerjudge.status import Status


class TestProcessor(unittest.TestCase):

    def test_GCC(self):
        self.assertEqual(GCC(GCC.Language.c, 4.8).image, 'gcc:4.8')
        self.assertEqual(GCC(GCC.Language.c, '4.8').image, 'gcc:4.8')
        self.assertEqual(GCC(GCC.Language.c).source, GCC('c').source)
        self.assertEqual(GCC(GCC.Language.c).source, GCC('C').source)
        self.assertEqual(GCC(GCC.Language.cpp).source, GCC('cpp').source)
        self.assertEqual(GCC(GCC.Language.cpp).source, GCC('C++').source)
        self.assertEqual(GCC(GCC.Language.cpp).source, GCC('c++').source)
        self.assertEqual(GCC(GCC.Language.go).source, GCC('go').source)
        self.assertEqual(GCC(GCC.Language.go).source, GCC('Go').source)
        self.assertEqual(GCC(GCC.Language.c).compile[0], 'gcc')
        self.assertEqual(GCC(GCC.Language.cpp).compile[0], 'g++')
        self.assertEqual(GCC(GCC.Language.go).compile[0], 'gccgo')

    def test_Go(self):
        self.assertEqual(Go(1).image, Go('1').image)
        self.assertEqual(Go('1').image, 'golang:1')
        self.assertEqual(Go(None, {'src': 'golang.go'}).source, 'golang.go')
        self.assertEqual(Go(None, {'bin': 'golang'}).judge, './golang')

    def test_PyPy(self):
        self.assertEqual(PyPy().compile, PyPy(3).compile)
        self.assertEqual(PyPy().judge, PyPy(3).judge)

    def test_mono(self):
        self.assertTrue(Mono(Mono.Language.csharp).source.endswith('.cs'))
        self.assertEqual(Mono().source, Mono(Mono.Language.csharp).source)


class TestDockerJudge(unittest.TestCase):

    def test_judge(self):
        result = judge(
            GCC('c', '4.8'),
            b'''
                #include <stdio.h>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])
        self.assertFalse(result[1])

    def test_CE(self):
        result = judge(
            GCC('c', '4.8'),
            b'''
                #include <cstdio>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'1 2', b'0.5')]
        )
        self.assertEqual(result[0][0][0], Status.CE)
        self.assertEqual(result[0][1][0], Status.CE)
        self.assertTrue(result[1])
        self.assertFalse(result[0][0][1][0])
        self.assertFalse(result[0][0][1][1])
        self.assertFalse(result[0][1][1][0])
        self.assertFalse(result[0][1][1][1])

    def test_TLE(self):
        result = judge(
            GCC('cpp', '4.8'),
            b'''
                #include <cstdio>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    while (true)
                        ;
                }
            ''',
            [(b'1 1', b'1'), (b'0 0', b'')],
            {'limit': {'time': .5}}
        )
        self.assertEqual(result[0][0][0], Status.TLE)
        self.assertEqual(result[0][1][0], Status.RE)
        self.assertAlmostEqual(result[0][0][2], .5, 0)
        self.assertAlmostEqual(result[0][1][2], .0, 0)
        self.assertFalse(result[1])

    def test_iofile(self):
        result = judge(
            GCC('c', '4.8'),
            b'''
                #include <stdio.h>
                int main() {
                    freopen("in.txt", "r", stdin);
                    freopen("out.txt", "w", stdout);
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')],
            {'iofilename': {'in': 'in.txt', 'out': 'out.txt'}}
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])
        self.assertFalse(result[1])

    def test_ONF(self):
        result = judge(
            GCC('c', '4.8'),
            b'''
                #include <stdio.h>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'0 0', b'')],
            {'iofilename': {'out': 'out.txt'}}
        )
        self.assertEqual(result[0][0][0], Status.ONF)
        self.assertEqual(result[0][1][0], Status.RE)
        self.assertTrue(result[0][1][1][1])
        self.assertFalse(result[1])

    def test_callback(self):
        def compiling_callback(code, stderr):
            self.assertFalse(code)
            self.assertFalse(stderr)

        def judging_callback(id, status,  # pylint: disable = W0622
                             stderr, duration):  # pylint: disable = W0613
            statuses = [Status.AC, Status.WA, Status.RE]
            self.assertEqual(status, statuses[id])

        result = judge(
            GCC('c', '4.8'),
            b'''
                #include <stdio.h>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')],
            {'callback': {'compile': compiling_callback,
                          'judge': judging_callback}}
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertFalse(result[1])

    def test_threads(self):
        t = time()
        result = judge(
            GCC('cpp', '4.8'),
            b'''
            int main() {
                while (true)
                    ;
            }
            ''',
            [(b'', b'')] * 3,
            {'limit': {'time': 5}, 'threads': 2}
        )
        self.assertEqual(result[0][0][0], Status.TLE)
        self.assertEqual(result[0][1][0], Status.TLE)
        self.assertEqual(result[0][2][0], Status.TLE)
        self.assertAlmostEqual(result[0][0][2], 5, 0)
        self.assertAlmostEqual(result[0][1][2], 5, 0)
        self.assertAlmostEqual(result[0][2][2], 5, 0)
        self.assertFalse(result[1])
        self.assertGreater(time() - t, 10)


class TestLlvmClang(unittest.TestCase):

    def test_llvm_clang_10(self):
        result = judge(
            Clang('c', 10),
            b'''
                #include <stdio.h>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])
        self.assertFalse(result[1])

    def test_llvm_clang_11(self):
        result = judge(
            Clang('c', 11),
            b'''
                #include <stdio.h>
                int main() {
                    int a, b;
                    scanf("%d %d", &a, &b);
                    printf("%d", a / b);
                    return 0;
                }
            ''',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])
        self.assertFalse(result[1])


class TestPython(unittest.TestCase):

    def test_python2(self):
        result = judge(
            Python('2'),
            b'a, b = [int(i) for i in raw_input().split()]; print a / b',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])

    def test_python3(self):
        result = judge(
            Python('3'),
            b'a, b = [int(i) for i in input().split()]; print(a / b)',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.WA)
        self.assertEqual(result[0][1][0], Status.AC)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])

    def test_CE(self):
        result = judge(
            Python('3'),
            b'import',
            [(b'', b''), (b'', b'')]
        )
        self.assertEqual(result[0][0][0], Status.CE)
        self.assertEqual(result[0][1][0], Status.CE)
        self.assertTrue(result[1])
        self.assertFalse(result[0][0][1][0])
        self.assertFalse(result[0][0][1][1])
        self.assertFalse(result[0][1][1][0])
        self.assertFalse(result[0][1][1][1])

    def test_processor_tuple(self):
        result = judge(
            ('Python', ('3',)),
            b"print('Hello, world!')",
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)

    def test_processor_dict(self):
        result = judge(
            ('Python', {'version': '3'}),
            b"print('Hello, world!')",
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)

    def test_pypy(self):
        result = judge(
            PyPy(2),
            b'a, b = [int(i) for i in raw_input().split()]; print a / b',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.AC)
        self.assertEqual(result[0][1][0], Status.WA)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])

    def test_pypy3(self):
        result = judge(
            PyPy(3),
            b'a, b = [int(i) for i in input().split()]; print(a / b)',
            [(b'1 1', b'1'), (b'1 2', b'0.5'), (b'0 0', b'')]
        )
        self.assertEqual(result[0][0][0], Status.WA)
        self.assertEqual(result[0][1][0], Status.AC)
        self.assertEqual(result[0][2][0], Status.RE)
        self.assertTrue(result[0][2][1][1])


class TestGoLang(unittest.TestCase):

    def test_go(self):
        result = judge(
            Go(1),
            br'''
                package main

                import "fmt"

                func main() {
                    fmt.Printf("hello, world\n")
                }
            ''',
            [(b'', b'hello, world')]
        )
        self.assertEqual(result[0][0][0], Status.AC)

    def test_gccgo(self):
        result = judge(
            GCC('go', 4.9),
            b'package main\n'

            b'import "fmt"\n'

            b'func main() {\n'
            br'    fmt.Printf("hello, world\n")'b'\n'
            b'}\n',
            [(b'', b'hello, world\n')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


class TestJava(unittest.TestCase):

    def test_openjdk(self):
        result = judge(
            OpenJDK(),
            b'''
                public class Main {
                    public static void main(String[] args) {
                        System.out.println("Hello, world!");
                    }
                }
            ''',
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


class TestNode(unittest.TestCase):

    def test_nodejs(self):
        result = judge(
            Node(12),
            b'console.log("Hello World")',
            [(b'', b'Hello World')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


class TestShell(unittest.TestCase):

    def test_bash(self):
        result = judge(
            Bash(),
            b'echo Hello, world!',
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


class TestPHP(unittest.TestCase):

    def test_php(self):
        result = judge(
            PHP(),
            b'<?php echo "Hello, world!";',
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


class TestRuby(unittest.TestCase):

    def test_ruby(self):
        result = judge(
            Ruby(),
            b'print "Hello, world!";',
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


class TestDotNet(unittest.TestCase):

    def test_csharp(self):
        result = judge(Mono(Mono.Language.csharp), b'''
            using System;

            public class HelloWorld
            {
                public static void Main(string[] args)
                {
                    Console.WriteLine ("Hello Mono World");
                }
            }
        ''', [(b'', b'Hello Mono World')])
        self.assertEqual(result[0][0][0], Status.AC)

    def test_vb(self):
        result = judge(Mono(Mono.Language.vb), b'''
            Imports System

            Module HelloWorld
                Sub Main()
                    Console.WriteLine("Hello World!")
                End Sub
            End Module
        ''', [(b'', b'Hello World!')])
        self.assertEqual(result[0][0][0], Status.AC)


class TestSwift(unittest.TestCase):

    def test_swiftc(self):
        result = judge(
            Swift(),
            b'print("Hello, world!")',
            [(b'', b'Hello, world!')]
        )
        self.assertEqual(result[0][0][0], Status.AC)


if __name__ == '__main__':
    unittest.main()
