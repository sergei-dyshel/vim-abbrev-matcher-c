# ============================================================================
# FILE: matcher_cpsm.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import globruntime, error, convert2fuzzy_pattern
import sys
import os
import os.path
from abbrev_matcher_c import match as match_c

def match(pattern, string, ispath):
    def normalize(score):
        score = float(score)
        return score * (len(string) ** 0.05)
    if ispath:
        # big bonus for matches entirely in filenames
        score = match_c(pattern, os.path.split(string)[1])
        if score != -1:
            return normalize(score) / 10
    score = match_c(pattern, string)
    if score != -1:
        return normalize(score)
    return None



class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_abbrev'
        self.description = 'Abbreviation matcher'

        self.__initialized = False
        self.__disabled = False

    def filter(self, context):
        candidates = context['candidates']
        input = context['input']
        if not input or not candidates:
            return candidates

        ispath = os.path.exists(candidates[0]['word'])
        # for cand in candidates:
        #     cand['score'] = match(input, cand['word'], ispath)
            # if cand['score'] is not None:
                # with open('/tmp/denite', 'a') as f:
                #     print(cand['score'], input, cand['word'], file=f)
        return [cand for cand in candidates if match(input, cand['word'], ispath) is not None]

    def convert_pattern(self, input_str):
        return ''

