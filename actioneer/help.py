class StringHelpCommand:
    """For if the entire output will only be a string"""
    def get_actions(self):
        ...

    def filter_actions(self, actions):
        ...

    def format_message(self, actions):
        ...

    def get_action_usage(self, action):
        ...

    def send_help(self, string):
        ...

    def no_action_found(self, name):
        ...

    

class CustomFormatHelpCommand:
    """For when the output isnt a string, usefull for when not outputting to the terminal"""
