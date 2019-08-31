from typing import Callable, Any, List, Dict
from inspect import Parameter, signature
from .utils import identity, bool_from_str
from .argument import Argument
from .errors import AlreadyAActionWithThatName


class Command:
    def __init__(self, func, aliases: List[str] = [], *,
                 options: Dict[str, Callable] = {},
                 options_aliases: Dict[str, str] = {}, flags: List[str] = [],
                 flags_aliases: Dict[str, str] = {}, performer=None):

        self.subs = {}
        self.name = func.__name__
        self.description = func.__doc__
        self.func = func
        self.aliases = aliases
        self.casts = [self.get_cast(param.annotation)
                      for param in signature(func).parameters.values()
                      if param.kind in (Parameter.POSITIONAL_OR_KEYWORD,
                                        Parameter.VAR_POSITIONAL)]
        self.options = options
        self.options_aliases = options_aliases
        self.flags = flags
        self.flags_aliases = flags_aliases
        self.error_handler = None
        self.performer = performer

    overrides = {
        Parameter.empty: identity,
        bool: bool_from_str
    }

    def get_cast(self, param):
        return self.overrides.get(param, param)

    def make_cast(self, args):
        return [cast(arg) for arg, cast in zip(args, self.casts)]

    def invoke(self, args: List[str] = [], ctx: List[Any] = []):
        ctx = {type(a): a for a in ctx}
        if len(args) >= 1:
            sub = self.subs.get(args[0])
            if sub:
                return sub.invoke(args[1:], ctx)
        try:
            name_annots = {name: v.annotation for name, v in
                           signature(self.func).parameters.items()
                           if v.kind == Parameter.KEYWORD_ONLY}

            ctxs = {name: ctx[value] for name, value in name_annots.items()}
            args = self.make_cast(args)
            self.func(*args, **ctxs)
        except Exception as e:
            if self.error_handler:
                self.run_fail(e, ctx)
            elif self.performer:
                self.performer.run_fail(e, ctx)

    def sub_command(self, aliases: list = []):
        def wrapper(func):
            if func.__name__ in self.subs.keys():
                raise AlreadyAActionWithThatName(func.__name__, self.name)
            for name in aliases + [func.__name__]:
                sub = Command(func)
                self.subs[name] = sub
            return sub
        return wrapper

    @property
    def parameters(self):
        return [Argument(param.name, param.annotation)
                for param in signature(self.func).parameters.values()
                if param.kind == Parameter.VAR_POSITIONAL]

    def error(self, func):
        self.error_handler = func

    def run_fail(self, e, ctx: Dict[Any, Any] = []):
        name_annots = {name: v.annotation for name, v in
                       signature(self.error_handler).parameters.items()
                       if v.kind == Parameter.KEYWORD_ONLY}

        ctxs = {name: ctx[value] for name, value in name_annots.items()}
        self.error_handler(e, **ctxs)
