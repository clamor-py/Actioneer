from typing import Callable, Any, List, Dict, Union
from inspect import Parameter, signature, iscoroutinefunction
from .utils import identity, bool_from_str, get_ctxs
from .argument import Argument
from .errors import AlreadyAActionWithThatName, CheckFailed


class Action:
    def __init__(self, func, aliases: List[str] = [], *,
                 name: str = None, flags: List[str] = [],
                 options: Dict[str, Callable] = {},
                 options_aliases: Dict[str, str] = {},
                 flags_aliases: Dict[str, str] = {},
                 checks: List[Callable] = []):

        self.subs = {}
        self.name = name or func.__name__
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
        self.performer = None
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
            if iscoroutinefunction(check) and await check(**ctxs):
                pass
            elif check(**ctxs):
                pass
            else:
                raise CheckFailed(f"Check {check.__name__} Failed")

    def get_cast(self, param):
        return self.overrides.get(param, param)

    def make_cast(self, args, ctx):
        out = []
        for arg, cast in zip(args, self.casts):
            if getattr(cast, "__origin__", "") is Union:
                for union_cast in cast.__args__:
                    try:
                        
                        out.append(union_cast(arg, **get_ctxs(union_cast, ctx)))
                        break
                    except ValueError:
                        continue
            out.append(cast(arg))

        return out

    async def async_make_cast(self, args, ctx):
        out = []
        for arg, cast in zip(args, self.casts):
            if getattr(cast, "__origin__", "") is Union:
                for union_cast in cast.__args__:
                    try:
                        if iscoroutinefunction(union_cast):
                            out.append(await union_cast(arg, **get_ctxs(union_cast, ctx)))
                            break
                        else:
                            out.append(union_cast(arg, **get_ctxs(union_cast, ctx)))
                            break
                    except ValueError:
                        continue
                continue
            if iscoroutinefunction(cast):
                out.append(await cast(arg, **get_ctxs(cast, ctx)))
            else:
                out.append(cast(arg, **get_ctxs(cast, ctx)))

        return out

    async def async_invoke(self, args: List[str] = [], ctxs: List[Any] = []):
        if len(args) >= 1:
            sub = self.subs.get(args[0])
            if sub:
                return await sub.async_invoke(args[1:], ctxs)
        try:
            await self.async_can_run(ctxs)
            ctx = get_ctxs(self.func, ctxs)
            args = await self.async_make_cast(args, ctxs)
            await self.func(*args, **ctx)
        except Exception as e:
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
            args = self.make_cast(args, ctxs)
            self.func(*args, **ctx)
        except Exception as e:
            if self.error_handler:
                self.run_fail(e, ctxs)
            elif self.performer:
                self.performer.run_fail(e, ctxs)

    def subcommand(self, func, name=None, *, aliases: list = []):
        if func.__name__ in self.subs.keys():
            raise AlreadyAActionWithThatName(func.__name__, self.name)
        for name in aliases + [name or func.__name__]:
            sub = self.__class__(func)
            self.subs[name] = sub
        return sub

    @property
    def parameters(self):
        return [Argument(param.name, param.annotation)
                for param in signature(self.func).parameters.values()
                if param.kind == Parameter.VAR_POSITIONAL]

    def error(self, func):
        self.error_handler = func

    async def async_run_fail(self, e, ctx: List[Any] = []):
        ctxs = get_ctxs(self.error_handler, ctx)
        if iscoroutinefunction(self.error_handler):
            await self.error_handler(e, **ctxs)
        else:
            self.error_handler(e, **ctxs)

    async def run_fail(self, e, ctx: List[Any] = []):
        ctxs = get_ctxs(self.error_handler, ctx)
        self.error_handler(e, **ctxs)
