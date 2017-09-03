# ============================================================================
# FILE: sorter_rank.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# CONTRIBUTOR: David Lee
#              Jean Cavallo
# DESCRIPTION: Base code is from "sorter_selecta.py" in unite.vim
#              Scoring code by Gary Bernhardt
#     https://github.com/garybernhardt/selecta
# License: MIT license
# ============================================================================

import string
from .base import Base
from denite.util import split_input
from abbrev_matcher_c import rank as rank_c
import os.path

def rank(pattern, string, ispath):
    def normalize(score):
        score = float(score)
        return score * (len(string) ** 0.05)
    if ispath:
        # big bonus for matches entirely in filenames
        score = rank_c(pattern, os.path.split(string)[1])
        if score != -1:
            return normalize(score) / 10
    score = rank_c(pattern, string)
    if score != -1:
        return normalize(score)
    return None



class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'sorter_abbrev'
        self.description = 'Abbreviation rank sorter'

    def filter(self, context):
        # if len(context['input']) < 1:
        #     return context['candidates']
        # for c in context['candidates']:
        #     c['filter__rank'] = 0
        #
        # for pattern in split_input(context['input']):
        #     for c in context['candidates']:
        #         c['filter__rank'] += get_score(c['word'], pattern)
        candidates = context['candidates']
        if not candidates or not input:
            return candidates
        ispath = os.path.exists(candidates[0]['word'])
        # s = sorted(candidates,
        #               key=lambda x: rank(context['input'], x['word'], ispath))
        # with open('/tmp/denite', 'w') as f:
        #     f.writelines(c['word'] for c in s)
        # return s
        def func(cand):
            score = rank(context['input'], cand['word'], ispath) or 0
            return score

        return sorted(candidates, key=func)


