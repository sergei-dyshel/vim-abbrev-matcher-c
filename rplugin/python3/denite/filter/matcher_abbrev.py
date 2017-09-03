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
from abbrev_matcher_c import match

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
        return [cand for cand in candidates if match(input, cand['word'])]

    def convert_pattern(self, input_str):
        return ''

