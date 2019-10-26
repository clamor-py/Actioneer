import actioneer

handler = actioneer.Performer()


def math():
    pass


math = actioneer.Action(math, ["m"])


def add(a: int, b: int):
    print(a + b)


math.child(add, aliases=["a"])

handler.register(math)
handler.run("math add 1 5")
