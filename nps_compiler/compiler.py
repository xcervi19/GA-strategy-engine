from curses import wrapper
from warnings import resetwarnings
import nps_compiler.config as cfg
from nps_compiler.utils import getGenomParts
import talib as ta
from talib import abstract
import pandas as pd
import numpy as np
import operator
import functools

class Compiler:
    def __init__(self, df):
        self.df = df

    def enrich_params(fce):
        def wrapper(*args):
            for arg in args:
                print(arg)
            fce(*args)
        return wrapper
        

    @staticmethod
    def breakdown_strategy(sentense):
        arr = sentense.split('|')
        return {
            'formula': arr[:-3],
            'extremes': arr[-1],
            'baseExtreme': arr[-2],
            'params': arr[-3],
        }

    @staticmethod
    def extremes_to_dict(str):
        def get_extreme(ex):
            arr = ex.split('=')
            maxmin = arr[1].split(',')
            return arr[0], {'max': maxmin[0], 'min': maxmin[1]}

        extremes = {}
        for ex in str.split('&'):
            temp = get_extreme(ex)
            extremes[temp[0]] = temp[1]
        return extremes


    def df_xor(self , *cols):
        cols = list(cols)
        forProcess = self.df[cols].values.T
        return functools.reduce(
            lambda x, y: (((x == 1) & (y == 0)) | ((x == 0) & (y == 1)))
            if type(x) != None
            else x,
            forProcess,
        )

    def df_and(self, *cols):
        cols = list(cols)
        forProcess = self.df[cols].values.T
        return functools.reduce(
            lambda x, y: (x == 1) & (y == 1) if type(x) != None else x, forProcess
        )


    def df_or(self, *cols):
        cols = list(cols)
        forProcess = self.df[cols].values.T
        return functools.reduce(
            lambda x, y: (x == 1) | (y == 1) if type(x) != None else x, forProcess
        )

    def bool(self, col_name, direction):
        col = self.df[col_name]
        crossDirection = -1 if direction == "up" else 1
        diffedSr = np.diff(col, prepend=[0])
        return np.where(diffedSr == crossDirection, 1, 0)

    def split(self, col_name, factor, split_type):
        col = self.df[col_name]
        factor = float(factor)
        if split_type == "relative":
            if self.extremes != "nan":
                maxmin = self.extremes[col_name]
                min = float(maxmin["min"])
                max = float(maxmin["max"])
            else:
                min = float(col.min())
                max = float(col.max())
            th = min + ((max - min) * factor)
            return np.where(col > th, 1, 0)
        if split_type == "value":
            return np.where(col > factor, 1, 0)

    def compile(self, sentense, indicators):
        df = self.df

        st_chunk = Compiler.breakdown_strategy(sentense)
        st_functions = st_chunk['formula']
        # TODO: control none operation ?
        if st_chunk['extremes'] != 'nan':
            self.extremes = Compiler.extremes_to_dict(st_chunk['extremes'])
        else:
            self.extremes = 'nan'
        all_ta_indicators = ta.get_function_groups()
        all_ta_list_indicators = sum(all_ta_indicators.values(), [])

        def func_for_exec(func_name, col_selection):
            if hasattr(self, func_name):
                return getattr(self,func_name)
            if func_name in all_ta_list_indicators:
                return abstract.Function(func_name, df)
            if func_name in operator.__all__:
                return getattr(operator, func_name)
            if hasattr(df, func_name):
                return getattr(df[col_selection], func_name)
            if 'window' in func_name:
                return getattr(df[col_selection], 'rolling')

        def compute_genom(parts):
            #TODO: consdider -> don't control if any object has function, but create INHERITANCE and 
            #      deal with params separetly
            name = parts['name']
            args = parts['params'].split(',')
            col_selection = parts['colSelection'] if 'colSelection' in parts else None
            fce = func_for_exec(name, col_selection)
            if hasattr(self, name):
                return fce(*args)
            if name in operator.__all__:
                fce = getattr(operator, name)
                args = (df[c] for c in args)
                return fce(*args)

            int_args = tuple(int(p) for p in args)
            if name in all_ta_list_indicators:
                return fce(*int_args)
            if 'window' in name:
                fce_name = name.replace('window', '')
                return getattr(fce(*int_args), fce_name)()

        for item in st_functions:
            parts = getGenomParts(item)
            column_name = parts['colIndex']
            self.df[column_name] = compute_genom(parts)
        return self.df