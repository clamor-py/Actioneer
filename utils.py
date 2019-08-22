
def identity(value):
    return value


true_strings = frozenset(["true", "t", "yes", "y", "ye", "yeh", "yeah", "sure",
                          "✅", "on", "1"])
false_strings = frozenset(["false", "f", "no", "n", "nope", "nah", "❌", "off",
                           "0"])


def bool_from_str(self, inp):
    inp = inp.lower()
    if inp in self.false_strings:
        return False
    elif inp in self.true_strings:
        return True
    else:
        raise Exception("TODO")  # TODO
