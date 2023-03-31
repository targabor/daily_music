import sys


class Logger:
    """Basic logger class to hide ugly prints"""
    def error(message: str):
        """Print error as console message

        Args:
            message (str): error message you want to print
        """
        print(message, file=sys.stderr)

    def info(message: str):
        """Print info as console message

        Args:
            message (str): info message you want to print
        """
        print(message)
