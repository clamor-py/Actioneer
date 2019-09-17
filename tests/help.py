import actioneer


handler = actioneer.Performer()


def ping():
    """Prints Pong!"""
    print("pong!")


def add(a: int, b: int):
    """Adds two numbers together"""
    print(a + b)


def help(command=None):
    """Help command"""
    if command:
        command = handler.commands[command]
        print(f"command:\t{command.description}")
        return
    out = []
    for name, command in handler.commands.items():
        subs = ' - ' + ', '.join([sub.name for sub in command.subs]) if command.subs else ""
        out.append(f"{name}{subs}:\t{command.description}")
    print("\n".join(out))


ping = actioneer.Action(ping, ["p"])
add = actioneer.Action(add, ["a"])
help = actioneer.Action(help)
handler.register(add)
handler.register(ping)
handler.register(help)

handler.run("help")
