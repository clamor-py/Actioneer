from inspect import signature, Parameter
from typing import List, Any


def identity(value):
    return value


true_strings = frozenset(["true", "t", "yes", "y", "ye", "yeh", "yeah", "sure",
                          "✅", "on", "1"])
false_strings = frozenset(["false", "f", "no", "n", "nope", "nah", "❌", "off",
                           "0"])


def bool_from_str(inp):
    inp = inp.lower()
    if inp in false_strings:
        return False
    elif inp in true_strings:
        return True
    else:
        raise Exception("TODO")  # TODO


def get_ctxs(func, ctx: List[Any] = []):
    ctx = {type(a): a for a in ctx}

    name_annots = {name: v.annotation for name, v in
                   signature(func).parameters.items()
                   if v.kind == Parameter.KEYWORD_ONLY}

    ctxs = {name: ctx[value] for name, value in name_annots.items()}
    return ctxs
