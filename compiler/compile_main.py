from nps_compiler.compiler import Compiler
from data_loader.utils import load_data, load_strategy_formulas

def main():
    st_formulas = load_strategy_formulas()
    df = load_data()
    compiler = Compiler(df)
    result = compiler.compile(st_formulas[1], [])
    print(result)
    return


if __name__ == "__main__":
    main()
