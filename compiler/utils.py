import inspect

def get_talib_params(indicator_name):
    indicator_function = getattr(talib, indicator_name)
    sig = inspect.signature(indicator_function)
    params = sig.parameters
    params_dict = {param.name: param.default for param in params.values()}
    return params_dict


def getGenomParts(genom):
    parts = genom.split("=")
    if len(parts) == 5:
        return {
            "type": "generated-from-others",
            "name": parts[0],
            "colSelection": parts[1].split(","),
            "params": parts[2],
            "options": parts[3].split(","),
            "colIndex": parts[4],
        }
    elif len(parts) == 4:
        return {
            "type": "generated-from-others",
            "name": parts[0],
            "colSelection": parts[1].split(","),
            "params": parts[2],
            "colIndex": parts[3],
        }
    else:
        return {
            "type": "generated-from-base",
            "name": parts[0],
            "params": parts[1],
            "colIndex": parts[2],
        }


def getGenomAsString(parts):
    if parts["type"] == "generated-from-others":
        "=".join(
            [
                parts["name"],
                ",".join(parts["colSelection"]),
                parts["params"],
                parts["colIndex"],
            ]
        )
    else:
        "=".join([parts["name"], parts["params"], parts["colIndex"]])