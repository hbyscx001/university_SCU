#!/usr/bin/env python3
# coding:utf-8

import ..preprocess

class basic_model(object):
    def __init__(self, processer):
        self._processer = processer

    def build(self, pkts):
        pass

    def _detect(self, pkts):
        pass

    def monitor(self):
        pass

    def load_pcapfile(self, filepath):
        pass
