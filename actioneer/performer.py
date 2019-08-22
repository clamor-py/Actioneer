from typing import List, Any, Dict, Callable
from .errors import NoClosingQuote
from .flags import Flags
from .options import Options
import re
import inspect
import traceback
quoteRe = re.compile(r"[\"']")
chunk = re.compile(r"\S+")


class Performer:
    def __init__(self, ctx: List[Any] = []):
        self.commands = []
        self.lookup = {}
        self.ctx = ctx

    def register(self, cmd):
        self.commands.append(cmd)
        self.lookup[cmd.name] = cmd
        for alias in cmd.aliases:
            self.lookup[alias] = cmd
        return cmd

    def run(self, args, ctx: List[Any] = []):
        cmd = self.lookup.get(args.split(" ")[0])
        if cmd:
            try:
                args = self.split_args(args)
                options, args = self.get_options(args, cmd.options,
                                                 cmd.options_aliases)
                flags, args = self.get_flags(args, cmd.flags,
                                             cmd.flags_aliases)
                flags = Flags(flags)
                options = Options(options)
                return cmd.invoke(args[1:], ctx + self.ctx + [flags, options])
            except Exception as e:
                if cmd.error_handler:
                    cmd.run_fail(e, ctx)
                else:
                    self.run_fail(e, ctx)

    def error(self, func):
        self.fail = func

    def fail(self, e):
        traceback.print_exc()

    def run_fail(self, e, ctx: Dict[Any, Any] = {}):
        name_annots = {name: v.annotation for name, v in
                       inspect.signature(self.fail).parameters.items()
                       if v.kind == inspect.Parameter.KEYWORD_ONLY}

        ctxs = {name: ctx[value] for name, value in name_annots.items()}
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
                    aliases: Dict[str, str]) -> Dict[str, Any]:
        """Will get options, the return will be converted as setup"""
        out = {}
        for i, arg in enumerate(inp):
            name = arg[2:]
            if not arg.startswith("-"):
                continue
            try:
                if arg.startswith("-") and name in options.keys():
                    out[name] = options[name](inp[i+1])
                    del inp[i]
                    del inp[i]
                elif arg.startswith("-") and name in aliases.keys():
                    out[aliases[name]] = options[name](inp[i+1])
                    del inp[i]
                    del inp[i]
            except Exception as e:
                raise e
        return out, inp

    def get_flags(self, inp: List[str], flags: List[str],
                  aliases: Dict[str, str]) -> Dict[str, bool]:
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
