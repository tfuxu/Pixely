# Copyright (C) 2022 Gradience Team
# Copyright 2023, tfuxu <https://github.com/tfuxu>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

import logging
import traceback

from halftone.constants import build_type # pyright: ignore


class Logger(logging.getLoggerClass()):
    """
    This is a wrapper of `logging` module. It provides
    custom formatting for log messages.

    Attributes
    ----------
    issue_footer_levels : :class:`list`
        Custom list of levels on which to show issue footer.
        [Allowed values: warning, error, traceback_error, critical]
    formatter : :class:`dict`
        Custom formatter for the logger.
    """

    log_colors = {
        "debug": 32,
        "info": 36,
        "warning": 33,
        "error": 31,
        "critical": 41
    }

    log_format = {
        'fmt': '%(message)s'
    }

    issue_footer = "If you are reporting an issue, please copy the logs printed above to the issue body."

    issue_footer_levels = [
        "error",
        "traceback_error",
        "critical"
    ]

    def __set_traceback_info(self, exc: BaseException = None) -> str:
        if not exc:
            exc = sys.exc_info()[1]
        exception_info = ""

        exception_tb = self.get_traceback(exc)

        message_head = "\n\t\033[1mTraceback:\033[0m"
        message_body = f"\n\033[90m{exception_tb}\033[0m"
        message_body = message_body.replace("\n", "\n\t\t")

        exception_info = message_head + message_body

        return exception_info

    def __set_exception_info(self, exc: BaseException = None) -> str:
        if not exc:
            exc = sys.exc_info()[1]
        exception_info = ""

        message_head = "\n\t\033[1mException:\033[0m"
        message_body = f"\n{exc}"
        message_body = message_body.replace("\n", "\n\t\t")

        exception_info = message_head + message_body

        return exception_info

    def __set_level_color(self, level: str, message: str) -> None:
        color_id = self.log_colors[level]

        return f"[\033[1;{color_id}m{level.upper()}\033[0m] {message}"

    def __init__(self, issue_footer_levels: list = None, formatter: dict = None):
        """
        The constructor for Logger class.
        """

        super().__init__(name="Halftone")

        if issue_footer_levels:
            self.issue_footer_levels = issue_footer_levels

        if formatter is None:
            formatter = self.log_format
        formatter = logging.Formatter(**formatter)

        if build_type == "debug":
            self.root.setLevel(logging.DEBUG)
        else:
            self.root.setLevel(logging.INFO)
        self.root.handlers = []

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.root.addHandler(handler)

    def debug(self, message: str) -> None:
        self.root.debug(self.__set_level_color("debug", str(message)))

    def info(self, message: str) -> None:
        self.root.info(self.__set_level_color("info", str(message)))

    def warning(self, message: str, exc: BaseException = None,
                    show_exception: bool = False, show_traceback: bool = False) -> None:
        if show_exception:
            message += self.__set_exception_info(exc)
        if show_traceback:
            message += self.__set_traceback_info(exc)

        self.root.warning(self.__set_level_color("warning", str(message)))
        if "warning" in self.issue_footer_levels:
            self.print_issue_footer()

    def error(self, message: str, exc: BaseException = None,
                show_exception: bool = False, show_traceback: bool = False) -> None:
        if show_exception:
            message += self.__set_exception_info(exc)
        if show_traceback:
            message += self.__set_traceback_info(exc)

        self.root.error(self.__set_level_color("error", str(message)))
        if "error" in self.issue_footer_levels:
            self.print_issue_footer()

    def traceback_error(self, message: str, exc: BaseException = None,
                            show_exception: bool = False) -> None:
        if show_exception:
            message += self.__set_exception_info(exc)
        message += self.__set_traceback_info(exc)

        self.root.error(self.__set_level_color("error", str(message)))
        if "traceback_error" in self.issue_footer_levels:
            self.print_issue_footer()

    def critical(self, message: str, exc: BaseException = None,
                    show_exception: bool = False, show_traceback: bool = True) -> None:
        if show_exception:
            message += self.__set_exception_info(exc)
        if show_traceback:
            message += self.__set_traceback_info(exc)

        self.root.critical(self.__set_level_color("critical", str(message)))
        if "critical" in self.issue_footer_levels:
            self.print_issue_footer()

    def set_silent(self) -> None:
        self.root.handlers = []

    def print_issue_footer(self) -> None:
        self.root.info(self.__set_level_color("info", self.issue_footer))

    def get_traceback(self, exc: BaseException) -> str:
        traceback_list = traceback.format_exception(exc)
        exception_tb = "".join(traceback_list)

        return exception_tb


"""
Use for testing only.
How to execute: python -m halftone.backend.logger
"""
# pylint: disable=W0719,W0718,W0707
if __name__ == "__main__":
    logging = Logger()

    logging.info("This is an information.")
    logging.debug("This is a debug message.")

    try:
        raise ArithmeticError("Arithmetic Error")
    except Exception:
        try:
            raise Exception("General Exception")
        except Exception as e:
            logging.traceback_error("This is an test error.", exc=e, show_exception=True)

            print(f"Retrieved traceback: {logging.get_traceback(e)}")
