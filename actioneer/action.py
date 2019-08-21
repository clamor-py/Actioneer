from typing import Union, Callable, Any, List, Dict, Dict
from typing_extensions import Protocol, Annotated, TypeVar
import traceback
from inspect import Parameter, signature
from .utils import identity, bool_from_str
from .argument import Argument


class Command:
    def __init__(self, func, aliases:List[str] = [], *, options: Dict[str, Callable] = {}, options_aliases: Dict[str, str] = {},
                 flags: List[str] = [], flags_aliases: Dict[str, str] = {}):
        self.subs = {}
        self.name = func.__name__
        self.func = func
        self.aliases = aliases
        self.casts = [self.make_cast(param)
                      for param in signature(func).parameters.values()
                      if param.kind == Parameter.VAR_POSITIONAL]
        self.options = options
        self.options_aliases = options_aliases
        self.flags = flags
        self.flags_aliases = flags_aliases

    overrides = {
        Parameter.empty: identity,
        bool: bool_from_str
    }

    def make_cast(self, param):
        return self.overrides.get(param, param)

    def invoke(self, args: List[str] = [], ctx: List[Any] = []):  # [10, "a", Message, ...]
        ctx = {type(a): a for a in ctx}
        sub = self.subs.get(args[0])
        if sub:
            return sub.invoke(args[1:], ctx)
        try:
            name_annots = {name: v.annotation for name, v in
                           signature(self.func).parameters.items()
                           if v.kind == Parameter.KEYWORD_ONLY}

            ctxs = {name: ctx[value] for name, value in name_annots.items()}
            self.func(*args, **ctxs)
        except Exception as e:
            raise e

    def sub_command(self, aliases: list = []):
        def wrapper(func):
            if func.__name__ in self.subs.keys():
                raise Exception(func.__name__, self.name)  # TODO
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

    def error_handler(self, error):
        raise error  # TODO
