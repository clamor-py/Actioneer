import actioneer


handler = actioneer.Performer(["bruh"])


def test(a, b, *, message: str):
    print(a)
    print(b)
    print(message)


def check(*, message: str):
    print(message)
    return message == "bruh"


test = actioneer.Action(test, ["t"], checks=[check])
handler.register(test)

handler.run("test 1 2")