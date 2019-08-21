class Options:
    def __init__(self, options): self._options = options
    def __len__(self): return len(self._options)
    def __getitem__(self, key): return self._options[key]
    def __iter__(self): return iter(self._options)
    def __reversed__(): return reversed(self._options)
    def __contains__(self, k): return k in self._options
    def __repr__(self): return repr(self._options)
