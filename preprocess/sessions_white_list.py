#!/usr/env/bin python3
# -*- coding:utf-8 -*-

from scapy.all import *
from dpkt.ethernet import Ethernet
import binascii
from collections import defaultdict
from lxml import etree

from . import basic_process


class sswl(basic_process.Basic_processer):
    def __init__(self):
        pass

    def extract(self, PcapPath):
        res = defaultdict(lambda: defaultdict(set))
        reader = PcapReader(PcapPath)
        for pkt in reader:
            res[(pkt['TCP'].sport, pkt['TCP'].dport)][(pkt['IP'].src, pkt['IP'].dst)].add((pkt['Ethernet'].src, pkt['Ethernet'].dst))

        self._meta = res

        root = etree.Element("WHITE_LIST")
        for (tcp_src, tcp_dst), ip_data in self._meta.items():
            stream = etree.SubElement(root, "STREAM", port_from=str(tcp_src), port_to=str(tcp_dst))
            for (ip_src, ip_dst), eth_data in ip_data.items():
                ip_pair = etree.SubElement(stream, "IP", ip_from=ip_src, ip_to=ip_dst)
                for (eth_src, eth_dst) in eth_data:
                    etree.SubElement(ip_pair, "ETH", eth_from=eth_src, eth_to=eth_dst)
        self._xml_root = root

    def view(self):
        print(self._xml_root)

    def output(self, outFile):
        fd = open(outFile, 'wb')
        fd.write(etree.tostring(self._xml_root, pretty_print=True))

    def check(self, scapy_pkts):
        res = []
        for pkt in scapy_pkts:
            tcp_pair = (pkt['TCP'].sport, pkt['TCP'].dport)
            if tcp_pair not in self._meta.keys():
                res.append("Unknow TCP pair")
                continue
            ip_pair = (pkt['IP'].src, pkt['IP'].dst)
            if  ip_pair not in self._meta[tcp_pair].keys():
                res.append("Unknow IP pair")
                continue
            eth_pair = (pkt['Ethernet'].src, pkt['Ethernet'].dst)
            if eth_pair not in self._meta[tcp_pair][eth_pair]:
                res.append("Unknow ETH pair")
                continue
            res.append("Normal")
        return res




