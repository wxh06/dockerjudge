from time import time
import unittest

from dockerjudge import judge
from dockerjudge.processor import GCC
from dockerjudge.status import Status


class TestProcessor(unittest.TestCase):

    def test_GCC(self):
        self.assertEqual(GCC(GCC.Language.c).source, GCC('c').source)
        self.assertEqual(GCC(GCC.Language.c).source, GCC('C').source)
        self.assertEqual(GCC(GCC.Language.cpp).source, GCC('cpp').source)
        self.assertEqual(GCC(GCC.Language.cpp).source, GCC('C++').source)
        self.assertEqual(GCC(GCC.Language.c).compile[0], 'gcc')
        self.assertEqual(GCC(GCC.Language.cpp).compile[0], 'g++')


class TestDockerJudge(unittest.TestCase):

    def test_judge(self):
        result = judge(
            GCC('c', '4.9'),
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
        self.assertTrue(result[0][2][1])

    def test_CE(self):
        result = judge(
            GCC('c', '4.9'),
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
        self.assertEqual(result[1], result[0][0][1])
        self.assertEqual(result[0][0][1], result[0][1][1])

    def test_TLE(self):
        result = judge(
            GCC('cpp', '4.9'),
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
            {'limit': {'time': .1}}
        )
        self.assertEqual(result[0][0][0], Status.TLE)
        self.assertEqual(result[0][1][0], Status.RE)
        self.assertAlmostEqual(result[0][0][2], .1, 1)
        self.assertAlmostEqual(result[0][1][2], .0, 1)

    def test_iofile(self):
        result = judge(
            GCC('c', '4.9'),
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
        self.assertTrue(result[0][2][1])

    def test_onf(self):
        result = judge(
            GCC('c', '4.9'),
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
        self.assertTrue(result[0][1][1])


if __name__ == '__main__':
    unittest.main()
