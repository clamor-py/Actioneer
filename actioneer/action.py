from typing import Callable, Any, List, Dict, Union, Tuple
from inspect import Parameter, signature, iscoroutinefunction, isclass
from .utils import identity, bool_from_str, get_ctxs, Flags, Options
from .argument import Argument
from .errors import AlreadyAActionWithThatName, CheckFailed, RequiredArgumentMissing, ConvertingError
from copy import copy
# from .performer import Performer


def action(*args, **kwargs):
    if len(args) > 0 and callable(args[0]):
        return Action(*args, **kwargs)

    def _(fn):
        return Action(fn, *args, **kwargs)
    return _

async def awaitable(v):
    if hasattr(v, "__await__"):
        return await v
    else:
        return v

class Action:
    __slots__ = ["casts", "subs", "func", "description", "aliases", "options", "option_aliases", "flags", "flag_aliases",
                 "error_handler", "performer", "checks", "name"]

    def __init__(self, func, aliases: Tuple[str] = (), *,
                 name: str = None, flags: Tuple[str] = (),
                 options: Dict[str, Callable] = frozenset(),
                 option_aliases: Dict[str, str] = frozenset(),
                 flag_aliases: Dict[str, str] = frozenset(),
                 checks: Tuple[Callable] = (),
                 performer: "Performer" = None): # TODO
        if isclass(func):
            self.subs = {k: (Action(v) if not isinstance(v, Action) else v)
                         for k, v in vars(func).items() if not k.startswith("__")}
            self.func = copy(func.__call__)
        else:
            self.subs = {}
            self.func = func

        self.casts = [self.get_cast(param.annotation)
                      for param in signature(self.func).parameters.values()
                      if param.kind in [Parameter.POSITIONAL_OR_KEYWORD,
                                        Parameter.VAR_POSITIONAL]]

        self.name = name or func.__name__
        self.description = func.__doc__
        self.aliases = aliases

        self.options = options
        self.option_aliases = option_aliases
        self.flags = flags
        self.flag_aliases = flag_aliases
        self.error_handler = None
        self.performer = performer
        self.checks = checks

    overrides = {
        Parameter.empty: identity,
        bool: bool_from_str,
        Tuple: identity,
        List: identity
    }

    async def can_run(self, ctx: Tuple[Any] = ()):
        for check in self.checks:
            if not await awaitable(check(**get_ctxs(check, ctx))):
                raise CheckFailed(f"Check {check.__name__} Failed")

    def get_cast(self, param):
        return self.overrides.get(param, param)

    async def make_cast(self, args, ctx):
        out = []
        for arg, cast in zip(args, self.casts + ([self.casts[-1]]*(len(args) - len(self.casts)))):
            try:
                if getattr(cast, "__origin__", "") is Union:
                    for union_cast in cast.__args__:
                        try:
                            result = union_cast(arg, **get_ctxs(union_cast, ctx))
                            out.append((await result) if hasattr(result, "__await__") else result)
                            break
                        except ValueError:
                            continue
                    continue
                # elif hasattr(cast, "__origin__"):
                #     out.append(arg)
                result = cast(arg, **get_ctxs(cast, ctx))
                out.append((await result) if hasattr(result, "__await__") else result)
            except:
                raise ConvertingError("failed to convert from {} with {!r}".format(arg, cast))

        return out

    async def invoke(self, args: Tuple[str] = (), ctxs: Tuple[Any] = ()):
        print(1)
        if len(args) >= 1:
            print(2)
            sub = self.subs.get(args[0])
            if sub:
                options, args = self.performer.get_options(args, sub.options,
                                                           sub.option_aliases)
                flags, args = self.performer.get_flags(args, sub.flags,
                                                       sub.flag_aliases)
                flags = Flags(flags)
                options = Options(options)
                print(3)
                return await sub.invoke(args[1:], ctxs)
        try:
            if not len(args) >= len(list(filter(lambda a: not a.default, self.parameters))):
                raise RequiredArgumentMissing()
            await self.can_run(ctxs)
            ctx = get_ctxs(self.func, ctxs)
            args = await self.make_cast(args, ctxs)
            await self.func(*args, **ctx)
        except Exception as e:
            if self.error_handler:
                await self.run_fail(e, ctxs)
            elif self.performer:
                await self.performer.run_fail(e, ctxs)

    # def invoke(self, args: Tuple[str] = (), ctxs: Tuple[Any] = ()):
    #     if len(args) >= 1:
    #         sub = self.subs.get(args[0])
    #         if sub:
    #             options, args = self.performer.get_options(args, sub.options,
    #                                                        sub.option_aliases)
    #             flags, args = self.performer.get_flags(args, sub.flags,
    #                                                    sub.flag_aliases)
    #             flags = Flags(flags)
    #             options = Options(options)
    #             return sub.invoke(args[1:], ctxs + (flags, options))
    #     try:
    #         if len(args) != self.parameters:
    #             raise RequiredArgumentMissing()
    #         self.can_run(ctxs)
    #         ctx = get_ctxs(self.func, ctxs)
    #         args = self.make_cast(args, ctxs)
    #         self.func(*args, **ctx)
    #     except Exception as e:
    #         if self.error_handler:
    #             self.run_fail(e, ctxs)
    #         elif self.performer:
    #             self.performer.run_fail(e, ctxs)

    def child(self, *args, **kwargs):
        def wraps(func_class):
            kwargs["name"] = kwargs.get("name", func_class.__name__)
            if kwargs["name"] in self.subs.keys():
                raise AlreadyAActionWithThatName(kwargs["name"], self.name)
            sub = self.__class__(func_class, *args, **kwargs)
            self.subs[kwargs["name"]] = sub
            return sub

        if len(args) > 0 and callable(args[0]):
            command = args[0]
            args = args[1:]
            return wraps(command)
        return wraps

    @property
    def parameters(self):
        return [Argument(param.name, param.annotation, param.kind, param.default)
                for param in signature(self.func).parameters.values()
                if param.kind in [Parameter.POSITIONAL_OR_KEYWORD,
                                  Parameter.VAR_POSITIONAL]]


    def error(self, func):
        self.error_handler = func

    async def run_fail(self, e, ctx: Tuple[Any] = ()):
        await self.error_handler(e, **get_ctxs(self.error_handler, ctx))


    def __call__(self): pass
