from time import time
import unittest

from dockerjudge import judge


class TestDockerJudge(unittest.TestCase):

    def test_judge(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.c',
                        'compile': 'gcc a.c',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    long long a, b;''\n'
                       r'    scanf("%lld %lld", &a, &b);''\n'
                       r'    printf("%d\n", a / b);''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 1', '1'),
                        ('1 2', '0.5'),
                        ('1 0', '')])
        self.assertEqual(result[0][0][0], 'AC')
        self.assertEqual(result[0][1][0], 'WA')
        self.assertEqual(result[0][2][0], 'RE')
        self.assertFalse(result[1])

    def test_ce(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.cpp',
                        'compile': 'gcc a.cpp',
                        'judge': '%s/a.out'},
                       r'#include <iostream>''\n'
                       r'int main() {''\n'
                       r'    long long a, b;''\n'
                       r'    std::cin >> a >> b;''\n'
                       r'    std::cout << a + b;''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 2', '3')])
        self.assertEqual(result[0][0][0], 'CE')
        self.assertTrue(result[1])

    def test_tle(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.cpp',
                        'compile': 'g++ a.cpp',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    while (true)''\n'
                       r'        ;''\n'
                       r'}''\n',
                       [('', '')],
                       0.05)
        self.assertEqual(result[0][0][0], 'TLE')
        self.assertAlmostEqual(result[0][0][1], 0.05, 1)
        self.assertFalse(result[1])

    def test_before_judging(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.c',
                        'compile': 'gcc a.c',
                        'before_judging': 'rm {}/a.out',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    long long a, b;''\n'
                       r'    scanf("%lld %lld", &a, &b);''\n'
                       r'    printf("%d\n", a + b);''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 2', '3')])
        self.assertEqual(result[0][0][0], 'RE')
        self.assertFalse(result[1])

    def test_after_judging(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.c',
                        'compile': 'gcc a.c',
                        'judge': '%s/a.out',
                        'after_judging': 'rm a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    freopen("a.out", "w", stdout);''\n'
                       r'    long long a, b;''\n'
                       r'    scanf("%lld %lld", &a, &b);''\n'
                       r'    printf("%d\n", a + b);''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 2', '3')],
                       iofile=(None, 'a.out'))
        self.assertEqual(result[0][0][0], 'ONF')
        self.assertFalse(result[1])

    def test_iofile(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.c',
                        'compile': 'gcc a.c',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    freopen("a.in", "r", stdin);''\n'
                       r'    freopen("a.out", "w", stdout);''\n'
                       r'    long long a, b;''\n'
                       r'    scanf("%lld %lld", &a, &b);''\n'
                       r'    printf("%d\n", a / b);''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 1', '1'),
                        ('1 2', '0.5'),
                        ('1 0', '')],
                       iofile=('a.in', 'a.out'))
        self.assertEqual(result[0][0][0], 'AC')
        self.assertEqual(result[0][1][0], 'WA')
        self.assertEqual(result[0][2][0], 'RE')
        self.assertFalse(result[1])

    def test_onf(self):
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.c',
                        'compile': 'gcc a.c',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    long long a, b;''\n'
                       r'    scanf("%lld %lld", &a, &b);''\n'
                       r'    printf("%d\n", a / b);''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 1', '1'),
                        ('1 2', '0.5'),
                        ('1 0', '')],
                       iofile=(None, 'a.out'))
        self.assertEqual(result[0][0][0], 'ONF')
        self.assertEqual(result[0][1][0], 'ONF')
        self.assertEqual(result[0][2][0], 'RE')
        self.assertFalse(result[1])

    def test_callback(self):
        def compiling_callback(code, err):
            self.assertFalse(code)
            self.assertFalse(err)

        def judging_callback(id, status, duration):
            statuses = ['AC', 'WA', 'RE']
            self.assertEqual(status, statuses[id])

        result = judge({'image': 'gcc:4.8',
                        'source': 'a.c',
                        'compile': 'gcc a.c',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    long long a, b;''\n'
                       r'    scanf("%lld %lld", &a, &b);''\n'
                       r'    printf("%d\n", a / b);''\n'
                       r'    return 0;''\n'
                       r'}''\n',
                       [('1 1', '1'),
                        ('1 2', '0.5'),
                        ('1 0', '')],
                       callback={'compiling': compiling_callback,
                                 'judging': judging_callback})
        self.assertEqual(result[0][0][0], 'AC')
        self.assertEqual(result[0][1][0], 'WA')
        self.assertEqual(result[0][2][0], 'RE')
        self.assertFalse(result[1])

    def test_split(self):
        t = time()
        result = judge({'image': 'gcc:4.8',
                        'source': 'a.cpp',
                        'compile': 'g++ a.cpp',
                        'judge': '%s/a.out'},
                       r'#include <stdio.h>''\n'
                       r'int main() {''\n'
                       r'    while (true)''\n'
                       r'        ;''\n'
                       r'}''\n',
                       [('', '')] * 3,
                       3, split=2)
        self.assertEqual(result[0][0][0], 'TLE')
        self.assertEqual(result[0][1][0], 'TLE')
        self.assertEqual(result[0][2][0], 'TLE')
        self.assertGreater(time() - t, 6)
        self.assertFalse(result[1])


if __name__ == '__main__':
    unittest.main()
