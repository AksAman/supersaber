import logging


class ColorConsole2:
    """Text colors:
    grey red green yellow blue magenta cyan white
    Text highlights:
    on_grey on_red on_green on_yellow on_blue on_magenta on_cyan on_white
    Attributes:
    bold dark underline blink reverse concealed"""

    ENDC = "\033[0m"
    from termcolor import colored

    HEADER = colored("", color="magenta", on_color=None, attrs=["bold"]).split(ENDC)[0]
    OKBLUE = colored("", color="blue", on_color=None, attrs=None).split(ENDC)[0]
    OKCYAN = colored("", color="cyan", on_color=None, attrs=None).split(ENDC)[0]
    OKGREEN = colored("", color="green", on_color=None, attrs=None).split(ENDC)[0]
    DEBUG = colored("", color="grey", on_color=None, attrs=None).split(ENDC)[0]
    WARNING = colored("", color="yellow", on_color=None, attrs=None).split(ENDC)[0]
    ERROR = colored("", color="red", on_color=None, attrs=None).split(ENDC)[0]
    EXCEPTION = ERROR
    CRITICAL = colored("", color="white", on_color="on_red", attrs=None).split(ENDC)[0]
    BOLD = colored("", color=None, on_color=None, attrs=["bold"]).split(ENDC)[0]
    UNDERLINE = colored("", color=None, on_color=None, attrs=["underline"]).split(ENDC)[
        0
    ]

    LOG_COLORS = {
        "header": [HEADER],
        "info": [OKGREEN],
        "debug": [DEBUG],
        "warning": [WARNING],
        "debugv": [DEBUG],
        "error": [ERROR],
        "exception": [EXCEPTION],
        "critical": [CRITICAL, BOLD, UNDERLINE],
        "level 60": [DEBUG],
        "ending": [ENDC],
    }


class CallbackFilter(logging.Filter):
    """
    A logging filter that checks the return value of a given callable (which
    takes the record-to-be-logged as its only parameter) to decide whether to
    log a record.
    """

    def __init__(self, callback):
        self.callback = callback

    def filter(self, record):
        if self.callback(record):
            return 1
        return 0


class AppFilter(CallbackFilter):

    def filter(self, record: logging.LogRecord):
        max_len = 3
        short_filename_split = record.pathname.split("/")
        if len(short_filename_split) < max_len:
            record.short_filename = record.pathname
        else:
            record.short_filename = "/".join(short_filename_split[-max_len:])
        return True and super().filter(record)


class CustomFormatter(logging.Formatter):
    console_class = ColorConsole2

    def get_formatted(self, msg: str, levelname):
        header, msg = msg.split("#", maxsplit=1)
        header_prefix = self.console_class.HEADER
        header_formatted = f"{header_prefix}{header}{self.console_class.ENDC}"
        msg_prefix = (
            "".join(
                self.console_class.LOG_COLORS.get(
                    levelname.lower(), [self.console_class.OKBLUE]
                )
            ).strip()
            + self.console_class.BOLD
        )
        msg_suffix = "".join(
            self.console_class.LOG_COLORS.get("ending", [self.console_class.ENDC])
        )
        msg_formatted = f"{msg_prefix}{msg}{msg_suffix}"
        return f"{header_formatted}:{msg_formatted}"

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # self._style._fmt = self.get_format(record)

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        result = self.get_formatted(result, record.levelname)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] {%(short_filename)s:%(lineno)d} %(funcName)s # %(message)s"
LOGGING_DATE_FORMAT = "%d/%b/%Y %H:%M:%S"

formatter = CustomFormatter(LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)

# Step 2: Create a Handler
console_handler = logging.StreamHandler()

# Step 3: Set the Formatter to the Handler
console_handler.setFormatter(formatter)

# Step 4: Add the Handler to the Logger
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)
logger.addFilter(AppFilter(lambda record: record.pathname))

# Set the logging level
logger.setLevel(logging.DEBUG)
