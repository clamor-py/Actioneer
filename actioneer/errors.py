
class ConvertingError(Exception):
    """Raised when converting a argument failed"""


class NoClosingQuote(Exception):
    """No closing quote on your command arguments"""


class NoCommandFound(Exception):
    """No command has been found with that name"""


class AlreadyAActionWithThatName(Exception):
    """When A Action is trying to be created with a name of a Action
       with the same name"""
