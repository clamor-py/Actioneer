
class Argument:
    def __init__(self, name, hint):
        self.name = name
        self.hint = hint

    def __repr__(self):
        return f"<Argument name='{self.name}' typehint='{self.hint}'>"
