class ActionError(Exception):
    """Error to do with the Action's"""


class InvokeError(Exception):
    """When a error happens turning trying to invoke it"""


class ConvertingError(InvokeError):
    """Raised when converting a argument failed"""


class NoClosingQuote(InvokeError):
    """No closing quote on your command arguments"""


class NoActionFound(InvokeError):
    """No command has been found with that name"""


class AlreadyAActionWithThatName(ActionError):
    """When A Action is trying to be created with a name of a Action with the same name"""


class CheckFailed(ActionError):
    """Raised when a check for a command failed"""


class RequiredArgumentMissing(ActionError):
    """The Action is missing a argument when trying to invoke it"""
