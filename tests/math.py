import actioneer

handler = actioneer.Performer()


def math():
    pass


math = actioneer.Command(math, ["m"])


@math.sub_command(["a"])
def add(a: int, b: int):
    print(a + b)


handler.register(math)
handler.run("math add 1 5")
