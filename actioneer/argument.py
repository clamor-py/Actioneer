class Argument:
    def __init__(self, name, typehint):
        self.name = name
        self.typehint = typehint

    def __repr__(self):
        return f"<Argument name='{self.name}' typehint='{self.typehint}'>"
