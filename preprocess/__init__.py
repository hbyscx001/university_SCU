#!/usr/bin/env python3
# coding:utf-8

import logging
import abc
import dpkt

import pandas as pd
import seaborn as sns


logger = logging.getLogger("PREPROC")


class basic_processer(object):
    def __init__(self):
        pass

    ##
    # @brief 输入原始二进制数据，中间通过数据分析，最后输出处理后的dataframe
    @abc.abstractmethod
    def extract(self, pcap):
        pass

    @abc.abstractmethod
    def view(self):
        pass


if __name__ == '__main__':
    class example_processer(basic_processer):
        def extract(self, pcap):
            df_res = pd.DataFrame(columns=('length'))
            for timestamp, buf in pcap:
                length = dpkt.ethernet.Ethernet(buf).data.length
                df_res.loc[timestamp] = [length]
            self._df = df_res
            return df_res

        def view(self):
            sns.displot(self._df)
