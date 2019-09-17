import actioneer


handler = actioneer.Performer()


@handler.register
@actioneer.Action
def ping(arg1):
    print("pong!", arg1)


handler.run("ping hello")
