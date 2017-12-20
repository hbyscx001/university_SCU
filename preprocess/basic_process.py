#!/usr/bin/env python3
# coding:utf-8

import logging
import abc
import dpkt

import pandas as pd
import seaborn as sns


logger = logging.getLogger("PREPROC")


class Basic_processer(object):
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
            df = pd.DataFrame([ts for ts, *args in pcap], columns=('timestamp',))
            return df

        def view(self, dataframe):
            sns.distplot(dataframe)
