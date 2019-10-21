import actioneer


handler = actioneer.Performer([1, True])  # inits the command handler,
# the argument is preset contexts that will be passed to the command
# you can subclass Perfomer and overwride the "split_args", "get_options"
# and "get_flags"


def echo(a: list, *msg, message: str, flags: actioneer.Flags, options: actioneer.Options):  # kwargs will be treated as contexts that will be passed to the command, this system used the annotations to find what to set as what
    print(a)
    print(msg)
    print(message)
    print(flags)
    print(options)


# NOTE: all contexts are optional so you might set a context but it doesnt need to be set as a kwarg

# you can pass none to perfomer, its just used for global error handler
echo = actioneer.Command(echo, flags=["test"], options={"channel": int}, performer=handler)  # this will most likly be wrapped in other libs that use this
handler.register(echo)  # adds it to the command handler


echo.invoke(["hello", "hello", "world"], ["bruh (the 'message', kwarg", actioneer.Flags({"test": True}), actioneer.Options({"channel": 123})]) # cmd.invoke doesnt handle arg passing
handler.run("echo hello world -test --channel 123", ["bruh"])  # handler.run handles arg splitting and options and flags
#            ^ (1) ^ (2)       ^ (3)   ^ (4)           ^ (5)
# 1 - command name
# 2 - command args
# 3 - flag
# 4 - option
# 5 - extra command context's that can be set when being invoked, ie channel, message ect
