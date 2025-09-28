import json
import os
import re
import time
from logging import getLogger
from typing import Optional

from nltk.corpus import wordnet

from ...utils.common import get_root_dir


class Dealer:
    def __init__(self):
        self.logger = getLogger("lorelm.nlp.synonym")

        self.lookup_num = 100000000
        self.load_tm = time.time() - 1000000
        self.dictionary = None

        try:
            self.dictionary = json.load(
                open(get_root_dir("resources/nlp/synonyms.json"), "r")
            )
        except Exception:
            self.logger.warning("Missing synonyms.json")
            self.dictionary = {}

        if not len(self.dictionary.keys()):
            self.logger.warning("Fail to load synonyms")

    def lookup(self, tk, topn=8):
        if re.match(r"[a-z]+$", tk):
            res = list(
                set(
                    [
                        re.sub("_", " ", syn.name().split(".")[0])
                        # for syn in get_synsets(tk)
                        for syn in wordnet.synsets(tk)
                    ]
                )
                - set([tk])
            )
            return [t for t in res if t]

        self.lookup_num += 1
        res = self.dictionary.get(re.sub(r"[ \t]+", " ", tk.lower()), [])
        if isinstance(res, str):
            res = [res]
        return res[:topn]
