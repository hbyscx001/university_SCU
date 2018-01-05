#!/usr/bin/env python3
# -*- coding:utf8 -*-

import dpkt


class pcap_reader(object):
    def __init__(self, filepath):
        self.fh = open(filepath, 'rb')
        self.reader = dpkt.pcap.Reader(self.fh)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            for ts, buf in self.reader:
                yield ts, buf
        except StopIteration:
            self.reader = dpkt.pcap.Reader(self.fh)
            raise StopIteration
