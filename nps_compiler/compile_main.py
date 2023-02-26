from ctypes import resize
import numpy as np
import pandas as pd
import nps_compiler.config as cfg
from nps_compiler.compiler import Compiler


def load_strategy_formulas():
    st_data = pd.read_csv(cfg.ST_DATA_PATH, sep=",", header=0, usecols=cfg.CSVCOLS)
    st_formulas = st_data["formula"]
    return st_formulas.to_numpy()


def load_data():
    fileName = "data/csv/" + cfg.PAIR + cfg.TIMEFRAME + ".csv"
    return pd.read_csv(fileName, sep=",", header=0, usecols=cfg.PAIR_COLS).astype(
        {
            "Open": "float64",
            "Close": "float64",
            "High": "float64",
            "Low": "float64",
            "Volume": "float64",
        }
    ).rename(
        # index=str,
        columns={
             "Open": "open",
             "Close": "close",
             "High": "high",
             "Low": "low",
             "Volume": "volume",
        },
    )


def main():
    st_formulas = load_strategy_formulas()
    print(st_formulas[1])
    df = load_data()
    print(df)
    compiler = Compiler(df)
    result = compiler.compile(st_formulas[1], [])
    print(result)
    return


if __name__ == "__main__":
    main()
