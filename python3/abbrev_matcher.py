#!/usr/bin/env python

""" The MIT License (MIT)

Copyright (c) 2015 Sergei Dyshel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import os.path
import sys
import logging
import shlex
import subprocess
import distutils.spawn
import operator
import pipes

from abbrev_matcher_c import rank as rank_c

REGEX_DIALECTS = ['grep', 'vim']

log = logging.getLogger('abbrev_matcher')

def make_regex(pattern, dialect='grep', greedy=True, escape=False):
    """Build regular expression corresponding to `pattern`."""

    assert dialect in REGEX_DIALECTS
    vim = (dialect == 'vim')

    def re_group(r):
        if dialect == 'vim':
            return r'%(' + r + r')'
        return r'(' + r + r')'

    def re_or(r1, r2):
        return re_group(re_group(r1) + '|' + re_group(r2))

    def re_opt(r):
        return re_group(r) + '?'

    asterisk = '*' if greedy or not vim else '{-}'
    res = ''
    if vim:
        res += r'\v'
    if not vim:  # XXX: ^ does not work in vim hightlighting
        res += '^'
    for i, ch in enumerate(pattern):
        match_start = '\zs' if i == 0 and vim else ''

        if ch.isalpha():
            ch_lower = ch.lower()
            ch_upper = ch.upper()
            not_alpha = '[^a-zA-Z]'
            not_upper = '[^A-Z]'
            anycase = (re_opt(r'.{asterisk}{not_alpha}') + '{match_start}' +
                       '[{ch_lower}{ch_upper}]')
            camelcase = re_opt(r'.{asterisk}{not_upper}') + '{ch_upper}'
            ch_res = re_or(anycase, camelcase)
        elif ch.isdigit():
            ch_res = (re_opt(r'.{asterisk}[^0-9]') + '{match_start}{ch}')
        else:
            ch_res = r'.{asterisk}\{match_start}{ch}'
        res += ch_res.format(**locals())
    if vim:
        res += '\ze'
    if escape:
        res = res.replace('\\', '\\\\')
    return res


def rank(pattern, string, ispath=False, debug=False):
    def normalize(score):
        score = float(score)
        return score * (len(string) ** 0.05)
    if ispath:
        # big bonus for matches entirely in filenames
        score = rank(pattern, os.path.split(string)[1])
        if score is not None:
            return normalize(score) / 10
    score = rank_c(pattern, string, False, debug)
    if score != -1:
        return normalize(score)
    return None

def match(pattern, string, debug=False):
    return rank_c(pattern, string, True, debug) != -1
