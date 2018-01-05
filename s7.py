#!/usr/bin/env python3
# -*-coding:utf-8-*-

import struct

class S7ProtocolException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __repr__(self):
        return self.__class__.__name__ + self._msg

class S7Protocol(object):
    def __init__(self):
        pass

    def s7_check(self, ts, buf):
        eth = dpkt.ethernet.Ethernet(buf)
        if type(eth.data) is dpkt.ip.IP and type(eth.data.data) is dpkt.tcp.TCP:
            tcp_payload = eth.data.data.data
            *args, tpkt_payload = S7Protocol.tpkt_unpack(tcp_payload)
            *args, cotp_payload = S7Protocol.cotp_unpack(tpkt_payload)
            return S7Protocol.s7_unpack(cotp_payload)[-1]
        return None

    @staticmethod
    def tpkt_unpack(tcp_payload):
        if len(tcp_payload) < 4:
            raise S7ProtocolException("TCP payload hasn't enough size")
        version, reserved, length = struct.unpack("!BBH", tcp_payload[:4])
        if version == 0x03 and reserved == 0x00:
            tpkt_payload = tcp_payload[4:length]
            return (version, reserved, length, tpkt_payload)

    @staticmethod
    def cotp_unpack(tpkt_payload):
        if len(tcp_payload) < 3:
            raise S7ProtocolException("TPKT payload hasn't enough size")
        length, pdu_type, option = struct.unpack("!BBB", tpkt_payload[:3])
        cotp_data = struct.unpack("!{}s".format(length-2), tpkt_payload[3:length+1])
        cotp_payload = tpkt_payload[length+1:]
        return (length, pdu_type, option, cotp_data, cotp_payload)

    @staticmethod
    def s7_unpack(copt_payload):
        if len(copt_payload) < 10:
            raise S7ProtocolException("COTP payload hasn't enough size")
        proto_id, ROSCTR, reserved, data_unit, para_len, data_len = struct.unpack(
            "!BBHHHH", copt_payload[:10]
        )
        if proto_id != 0x32:
            raise S7ProtocolException("Not S7 protocol")
        return (proto_id, ROSCTR, data_unit, copt_payload)
