import actioneer


handler = actioneer.Performer()


def ping():
    print("pong!")


ping = actioneer.Command("ping", ["p"])
handler.register(ping)

handler.run("ping")
