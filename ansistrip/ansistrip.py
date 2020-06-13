#!/usr/bin/env python3

from re import compile

ansi_escape = compile(rb"(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])")


def ansi_strip(text: str) -> str:
    """
    This function remove the ANSI Escape codes of a string.

    :param text: str: Text.

    """
    return ansi_escape.sub(b"", text.encode()).decode()
