from compiler.compiler import Compiler
from visualization.viewer import Viewer
from data_loader.utils import load_data, load_strategy_formulas

def main():
    st_formulas = load_strategy_formulas()
    df = load_data()
    compiler = Compiler(df)
    result = compiler.compile(st_formulas[1], [])
    print(result)
    result = result.set_index('Time')
    for c in result.columns:
        result[c].fillna(value=result[c].mean(), inplace=True)
    result.dropna(axis=1, how='all', inplace=True)
    viewer = Viewer(result, st_formulas[1])

if __name__ == '__main__':
    main()