#!/usr/bin/env python3
# -*- coding:utf8 -*-

from collection import Counter


from . import basic_process
from . import s7
from . import pcap_reader


class gram_preprocess(basic_process.Basic_processer):
    def __init__(self, pcapfile):
        self.analyer = s7.S7Protocol()
        self.freq_items = Counter()
        self.N = 3
        self.pkts_reader = pcap_reader(pcapfile)

    def extract(self):
        for ts, buf in self.pkts_reader:
            try:
                raw_data = self.analyer.s7_check(ts, buf)
                self.got_gram_item(raw_data)
            except Exception:
                pass

    def view(self):
        pass

    def got_gram_item(self, raw_data):
        length = len(raw_data)
        self.freq_items.update([raw_data[i:i+self.N] for i in range(0, length-self.N)])



