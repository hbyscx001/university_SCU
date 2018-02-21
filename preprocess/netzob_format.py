# -*- coding:utf-8 -*-

from . import basic_process
from .. import s7
import collections
from tqdm import tqdm

from netzob.all import *
import pickle
from datetime import datetime

class Netzob_process(Exception):
    def __init__(self, msg):
        upper(self).__init__(msg)

def filter_s7(messages):
    anaylzer = s7.S7Protocol()

    for message in messages:
        try:
            anaylzer.s7_check(message.data)
        except s7.S7ProtocolException:
            messages.remove(message)

    return messages

def print_tree(tree):
    buff = []
    _print_tree(tree, buff, ' ', 0)
    print('\n'.join(buff))

def _print_tree(tree, buff, prefix, level):
    if isinstance(tree, dict):
        for k, v in tree.items():
            _print_tree(k, buff, prefix, level)
            if v:
                _print_tree(v, buff, prefix, level+1)
    elif isinstance(tree, list):
        for i in tree:
            _print_tree(i, buff, prefix, level)
    elif isinstance(tree, Field):
        buff.append('{}+- {}/'.format(prefix*level, repr(tree)))
    elif isinstance(tree, Symbol):
        buff.append('{}+- {}/messages_count:{}'.format(prefix*level, tree.name, len(tree.messages)))
    else:
        buff.append('{}+- {}/'.format(prefix*level, repr(tree)))


class Netzob_process(basic_process.Basic_processer):
    def __init__(self):
        pass

    def split_session(self, messages):
        if not messages:
            raise Netzob_process("Split empty message to sessions")

        session = Session(messages)
        if session.isTrueSession():
            sessions = [session]
        else:
            sessions = session.getTrueSessions()
        return sessions

    def anaylze_session(self, session):
        symbols_key_field = {}
        session_symbols = Format.clusterBySize(session.messages.values())
        list(map(lambda x: Format.splitAligned(x), session_symbols))
        for symbol in session_symbols:
            key_fields = Format.findKeyFields(symbol)
            symbols_key_field[symbol] = [key_field['keyField'] for key_field in key_fields] if key_fields else []
        return symbols_key_field

    def view(self):
        pass

    def extract(self, filepath):
        sessions_keys = {}
        messages = PCAPImporter.readFile(filepath).values()
        filter_s7(messages)
        self.sessions = self.split_session(messages)
        for session in tqdm(self.sessions):
            sessions_keys["-".join(session.getEndpointsList()[0])] = self.anaylze_session(session)
        return sessions_keys

    def output(self, infile, outflag=False, outfile=None):
        res_dict = collections.defaultdict(dict)
        sessions_model = self.extract(infile)
        for endpoints, symbols in sessions_model.items():
            for symbol, fields in symbols.items():
                if fields:
                    fields_features = [field_obj.getValues() for field_obj in fields]
                    timestamp = [msg.date for msg in fields[0].messages]
                    res_dict[endpoints][symbol.name] = list(zip(timestamp,*fields_features))
                else:
                    field_features = symbol.getValues()
                    timestamp = [msg.date for msg in symbol.messages]
                    res_dict[endpoints][symbol.name] = list(zip(timestamp,field_features))

        if outflag:
            outfile = outfile if outfile else './' + datetime.now().strftime('%Y-%m-%d %H:%M.pickle')
            with open(outfile, 'wb') as f:
                pickle.dump(res_dict, f)
            print('Save to {}'.format(outfile))
        else:
            return res_dict

    def markov_output(self, output_dict):
        markov_res = collections.defaultdict(dict)
        for endpoint, session in output_dict.items():
            for symbol_name, samples in session.items():
                if len(samples) > 1:
                    X = samples[:-1]
                    Y = [sample[1:] for sample in samples[1:]]
                    markov_res[endpoint][symbol_name] = [(X[i], Y[i]) for i in range(len(X))]
                else:
                    markov_res[endpoint][symbol_name] = samples

        return markov_res



