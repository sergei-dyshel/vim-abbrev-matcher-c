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
from abbrev_matcher import rank
import os.path


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'sorter_abbrev'
        self.description = 'Abbreviation rank sorter'

    def filter(self, context):
        candidates = context['candidates']
        if not candidates or not input:
            return candidates
        ispath = os.path.exists(candidates[0]['word'])
        def func(cand):
            score = rank(context['input'], cand['word'], ispath=ispath) or 0
            return score

        return sorted(candidates, key=func)


