from typing import Callable, Any, List, Dict
from inspect import Parameter, signature, isawaitable
from .utils import identity, bool_from_str, get_ctxs
from .argument import Argument
from .errors import AlreadyAActionWithThatName, CheckFailed


class Command:
    def __init__(self, func, aliases: List[str] = [], *,
                 options: Dict[str, Callable] = {},
                 options_aliases: Dict[str, str] = {}, flags: List[str] = [],
                 flags_aliases: Dict[str, str] = {}, performer=None,
                 checks: List[Callable] = []):

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
        self.checks = checks

    overrides = {
        Parameter.empty: identity,
        bool: bool_from_str
    }

    def can_run(self, ctx: List[Any] = []):
        for check in self.checks:
            ctxs = get_ctxs(check, ctx)
            if check(**ctxs):
                pass
            else:
                raise CheckFailed(f"Check {check.__name__} Failed")

    async def async_can_run(self, ctx: List[Any] = []):
        for check in self.checks:
            ctxs = get_ctxs(check, ctx)
            if isawaitable(check) and await check(ctxs):
                pass
            elif check(ctxs):
                pass
            else:
                raise CheckFailed(f"Check {check.__name__} Failed")

    def get_cast(self, param):
        return self.overrides.get(param, param)

    def make_cast(self, args):
        return [(cast(arg)) if isawaitable(cast) else cast(arg)
                for arg, cast in zip(args, self.casts)]

    async def async_make_cast(self, args):
        return [(await cast(arg)) if isawaitable(cast) else cast(arg)
                for arg, cast in zip(args, self.casts)]

    async def async_invoke(self, args: List[str] = [], ctxs: List[Any] = []):
        if len(args) >= 1:
            sub = self.subs.get(args[0])
            if sub:
                return await sub.async_invoke(args[1:], ctxs)
        try:
            await self.async_can_run(ctxs)
            ctx = get_ctxs(self.func, ctxs)
            args = await self.async_make_cast(args)
            await self.func(*args, **ctx)
        except Exception as e:
            raise e
            if self.error_handler:
                await self.async_run_fail(e, ctxs)
            elif self.performer:
                await self.performer.async_run_fail(e, ctxs)

    def invoke(self, args: List[str] = [], ctxs: List[Any] = []):
        if len(args) >= 1:
            sub = self.subs.get(args[0])
            if sub:
                return sub.invoke(args[1:], ctxs)
        try:
            self.can_run(ctxs)
            ctx = get_ctxs(self.func, ctxs)
            args = self.make_cast(args)
            self.func(*args, **ctx)
        except Exception as e:
            if self.error_handler:
                self.run_fail(e, ctxs)
            elif self.performer:
                self.performer.run_fail(e, ctxs)

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

    async def async_run_fail(self, e, ctx: List[Any] = []):
        ctxs = get_ctxs(self.error_handler, ctx)
        if isawaitable(self.error_handler):
            await self.error_handler(e, **ctxs)
        else:
            self.error_handler(e, **ctxs)

    async def run_fail(self, e, ctx: List[Any] = []):
        ctxs = get_ctxs(self.error_handler, ctx)
        self.error_handler(e, **ctxs)
