import functools
import matplotlib.pyplot as plt
from compiler.utils import getGenomParts

def processSplitTresholds(x, y, ff):
    if "split" in y:
        params = getGenomParts(y)['params'].split(',')
        print(params)
        oneCol = ff.loc[:, params[0]]
        min = float(oneCol.min())
        max = float(oneCol.max())
        x[params[0]] = min + ((max - min) * float(params[1]))
    return x

def reduceSplitTh(computeString, ffAll):
    return functools.reduce(
        lambda x, y: processSplitTresholds(x, y, ffAll), computeString.split("|"), {}
    )

def isInMeanTolerance(ref_mean, ref_var, df, col):
    firstSr = df.loc[:, col]
    mean = firstSr.mean()
    ratio_mean = abs(ref_mean / mean)

    var = firstSr.var()
    ratio_var = abs(ref_var / var)

    return (
        True
        if ratio_mean > 0.1
        and ratio_mean < 4
        and ratio_var > 0.1
        and ratio_var < 4
        else False
    )

def isNotSplit(df, col):
    firstSr = df.loc[:, col]
    new = firstSr[(firstSr != 1) & (firstSr != 0)]
    return False if new.empty else True

def getTreshholdInDimensions(col, tresholds):
    if col in tresholds:
        return tresholds[col]
    else:
        return False


class Viewer():
    def __init__(self, df, formula) -> None:
        self.plot_candles = False
        fig = plt.figure(figsize=(20, 8))
        fig.tight_layout()
        plt.subplots_adjust(wspace=0, hspace=0)
        self.plotCandles = True

        # ohlc = df.loc[:, ['Time', 'Open', 'High', 'Low', 'Close']]
        # ohlc['Time'] = pd.to_datetime(ohlc['Time'])
        # ohlc['Time'] = ohlc['Time'].apply(mpl_dates.date2num)
        # ohlc = ohlc.astype(float)

        print(df.columns)
        cols = [
            c for c in df.columns if c not in ["Time", "Open", "High", "Low"]
        ]
        cols = list(filter(isNotSplit, cols))
        cols.reverse()

        outerSeries = []
        while cols:
            colRef = cols.pop()
            if outerSeries and [True for s in outerSeries if colRef in s]:
                continue
            innerHead = [colRef]
            ref_mean = df.loc[:, colRef].mean()
            ref_var = df.loc[:, colRef].var()
            inner = list(filter(isInMeanTolerance, cols))
            print(inner)
            outerSeries.append(innerHead + inner)
            # break

        print(outerSeries)

        seriesMulti = list(
            map(lambda x: list(map(lambda y: df.loc[:, y], x)), outerSeries)
        )
        plotTypesMulti = list(
            map(lambda x: list(map(lambda y: "-", x)), outerSeries)
        )
        seriesMultiLen = len(seriesMulti)

        splitTh = reduceSplitTh(formula, df)
        seriesMultiTreshholds = list(
            map(
                lambda x: list(
                    map(lambda y: getTreshholdInDimensions(y, splitTh), x)
                ),
                outerSeries,
            )
        )
        figs = [[seriesMultiLen, 1, i + 1] for i in range(seriesMultiLen)]
        if not splitTh:
            print("WARMING >>> empty split, something is wrong")
