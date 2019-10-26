from typing import List, Any, Dict, Callable, Tuple
from .errors import NoClosingQuote
from .utils import get_ctxs, Flags, Options
from .action import Action
import re
import traceback
from inspect import isawaitable


quoteRe = re.compile(r"[\"']")
chunk = re.compile(r"\S+")


class Performer:
    def __init__(self, ctx: Tuple[Any, ...] = (), *, loop=None):
        self.commands = {}
        self.lookup = {}
        self.ctx = ctx + (self,)
        self.loop = loop

    def register(self, cmd):
        self.commands[cmd.name] = cmd
        self.lookup[cmd.name] = cmd
        cmd.performer = self
        for alias in cmd.aliases:
            self.lookup[alias] = cmd
        return cmd

    def run(self, args, ctx: Tuple[Any] = ()):
        cmd = self.lookup.get(args.split(" ")[0])
        if cmd:
            try:
                args = self.split_args(args)
                options, args = self.get_options(args, cmd.options,
                                                 cmd.option_aliases)
                flags, args = self.get_flags(args, cmd.flags,
                                             cmd.flag_aliases)
                flags = Flags(flags)
                options = Options(options)
                if self.loop:
                    coro = cmd.async_invoke(args[1:], ctx + self.ctx +
                                            (flags, options))
                    return self.loop.create_task(coro)
                else:
                    return cmd.invoke(args[1:], ctx + self.ctx +
                                      (flags, options))
            except Exception as e:
                if self.loop:
                    if cmd.error_handler:
                        self.loop.create_task(cmd.async_run_fail(e, ctx))
                    else:
                        self.loop.create_task(self.async_run_fail(e, ctx))
                else:
                    if cmd.error_handler:
                        cmd.run_fail(e, ctx)
                    else:
                        self.run_fail(e, ctx)

    def error(self, func):
        self.fail = func

    def fail(self, e):
        traceback.print_exception(type(e), e, e.__traceback__)

    def run_fail(self, e, ctx: Tuple[Any] = ()):
        ctxs = get_ctxs(self.fail, ctx)
        self.fail(e, **ctxs)

    async def async_run_fail(self, e, ctx: List[Any] = ()):
        ctxs = get_ctxs(self.fail, ctx)
        if isawaitable(self.fail):
            await self.fail(e, **ctxs)
        else:
            self.fail(e, **ctxs)

    def split_args(self, s: str) -> List[str]:
        """Will split the raw input into the arguments"""
        args = []
        i = 0
        while i < len(s):
            char = s[i]
            if re.match(quoteRe, char):
                try:
                    j = s.index(char, i+1)
                    args.append(s[i + 1: j])
                    i = j
                except ValueError:
                    raise NoClosingQuote("Missing closing quote.")
            else:
                match = chunk.match(s, i)
                if match:
                    args.append(match.group())
                    i = match.end()
            i += 1
        return args

    def get_options(self, inp: List[str], options: Dict[str, Callable],
                    aliases: Dict[str, str]) -> Tuple[Dict[str, bool], List[str]]:
        """Will get options, the return will be converted as setup"""
        options_out = {}
        for i, arg in enumerate(inp):
            name = arg[2:]
            if not arg.startswith("-"):
                continue
            try:
                if arg.startswith("-") and name in options.keys():
                    options_out[name] = options[name](inp[i+1])
                    del inp[i]
                    del inp[i]
                elif arg.startswith("-") and name in aliases.keys():
                    options_out[aliases[name]] = options[name](inp[i+1])
                    del inp[i]
                    del inp[i]
            except Exception as e:
                raise e
        return options_out, inp

    def get_flags(self, inp: List[str], flags: List[str],
                  aliases: Dict[str, str]) -> Tuple[Dict[str, bool], List[str]]:
        """Will get all flags"""
        out = {name: False for name in flags}

        for i, arg in enumerate(inp):
            name = arg[1:]
            if arg.startswith("-") and name in flags:
                out[name] = True
                del inp[i]
            elif arg.startswith("-") and name in aliases.keys():
                out[aliases[name]] = True
                del inp[i]
        return out, inp
