from typing import List, Any, Dict, Callable, Tuple
from .errors import NoClosingQuote, NoActionFound
from .utils import get_ctxs, Flags, Options
from .action import Action
import re
import traceback
from inspect import isawaitable


quoteRe = re.compile(r"[\"']")
chunk = re.compile(r"\S+")


class SourceStr(str):
    pass


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

    async def run(self, args, ctx: Tuple[Any] = ()):
        cmd_name = args.split(" ")[0]
        cmd = self.lookup.get(cmd_name)
        try:
            if cmd:
                split_args = self.split_args(args)
                options, args = self.get_options(args, cmd.options,
                                                 cmd.option_aliases)
                flags, args = self.get_flags(args, cmd.flags,
                                             cmd.flag_aliases)
                flags = Flags(flags)
                options = Options(options)
                source = SourceStr(args[len(cmd_name):].lstrip())
                return await cmd.invoke(split_args[1:], ctx + self.ctx +
                                    (flags, options, source))
            raise NoActionFound("No Action called {} found".format(cmd_name))
        except Exception as e:
            if cmd and cmd.error_handler:
                return await cmd.run_fail(e, ctx)
            else:
                return await self.run_fail(e, ctx)

    def error(self, func):
        self.fail = func


    async def run_fail(self, e, ctx: List[Any] = ()):
        traceback.print_exception(type(e), e, e.__traceback__)

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
