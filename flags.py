class Flags:
    def __init__(self, flags):
        self._flags = flags

    def __len__(self):
        return len(self._flags)

    def __getitem__(self, key):
        return self._flags[key]

    def __iter__(self):
        return iter(self._flags)

    def __reversed__(self):
        return reversed(self._flags)

    def __contains__(self, k):
        return k in self._flags

    def __str__(self):
        return str(self._flags)
