class BaseTypehint:
    def __init__():
        pass

    def __getitem__(self, keys):
        self.types = keys

    def convert(self, arg):
        for type in self.types:
            try:
                if type is None:
                    return None
                return type(arg)
            except:
                pass


Union = BaseTypehint()


def a(b: Union[str, int]):
    pass
