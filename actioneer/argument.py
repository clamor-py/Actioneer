class Argument:
    def __init__(self, name, typehint, type, default):
        self.name = name
        self.typehint = typehint
        self.type = type
        self.default = default

    def __repr__(self):
        return f"<Argument name='{self.name}' typehint='{self.typehint}'>"
