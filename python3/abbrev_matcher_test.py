#!/usr/bin/env python3

import os.path
import unittest
from abbrev_matcher import rank, match


class BaseTest(unittest.TestCase):
    def assert_filter(self, pattern, matching=[], not_matching=[]):
        self.assertTrue(match(pattern, pattern))
        for m in matching:
            try:
                self.assertTrue(match(pattern, m))
            except AssertionError:
                print(pattern, m)
        for nm in not_matching:
            try:
                self.assertFalse(match(pattern, m))
            except AssertionError:
                print(pattern, m)

    def assert_ranked(self, pattern, strings, **kwargs):
        self.assert_filter(pattern, matching=strings)
        ranked = sorted(reversed(strings),
                        key=lambda s: rank(pattern, s, **kwargs))
        self.assertEqual(ranked, strings)

    def assert_ranked_files(self, pattern, path_lists):
        path_strings = [os.path.join(*p) for p in path_lists]
        self.assert_ranked(pattern, path_strings, ispath=True)


class TestMatch(BaseTest):
    def test_match_letters(self):
        self.assert_filter('abc',
                          matching=['abc', 'ABC', 'Abc', 'aBC', 'aBc', 'AbC'])
        self.assert_filter('abc',
                          matching=['a_b_c', 'A_B_C', 'aa_bc', 'aa_bb_cc'])
        self.assert_filter(
            'abc', matching=['AdBC', 'adBc'], not_matching=['ADbc'])

    def test_math_digits(self):
        self.assert_filter(
            'a1b',
            matching=['a_1b', 'a1_b', 'a1234b', 'a_1_b'],
            not_matching=['a21b'])

    def test_match_camel_case(self):
        # self.assert_filter('')
        pass

    def test_match_punct(self):
        self.assert_filter(
            'a/b', matching=['a / b', 'a//b', 'a./b'], not_matching=['ba/b'])


class TestRank(BaseTest):
    def test_line_length(self):
        self.assert_ranked('abc', ['abc', 'abc abc'])

    def test_basic(self):
        # prefer
        self.assert_ranked('foobar', ['foo_bar', 'some_foobar'])

        # consecutive subwords
        self.assert_ranked('fb', ['foo_bar_qux', 'foo_qux_bar'])
        self.assert_ranked('fb', ['qux_foo_bar', 'foo_qux_bar'])

        # same big word
        self.assert_ranked('fb', ['foo bar', 'foo_bar'])

        # letters starting big words
        self.assert_ranked('fq', ['for_bar qux', 'bar_foo qux'])


class TestRankFiles(BaseTest):
    def test_basic(self):
        # line length
        self.assert_ranked_files('fb', [['fb'], ['dir', 'fb']])

        # match within basename
        self.assert_ranked_files('fb', [['foo bar'], ['foo', 'bar']])


if __name__ == '__main__':
    unittest.main(verbosity=10, failfast=True)
