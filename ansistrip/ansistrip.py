#!/usr/bin/env python3

import re

__all__ = ["ansi_strip"]


# Matched on str, not bytes: the C1 class below means the code points
# U+0080-U+009F, which is what it is meant to cover. On bytes it would also
# match UTF-8 continuation bytes and corrupt any non-ASCII text.
ansi_escape: re.Pattern[str] = re.compile(
    r"""(?:
          # OSC: xterm takes both ST and BEL as terminators.
          (?: \x1B\] | \x9D )
          [^\x1B\x07\x9C]*
          (?: \x1B\\ | \x07 | \x9C )
          # DCS, SOS, PM and APC: ST only, so a BEL is part of the payload.
        | (?: \x1B[PX^_] | [\x90\x98\x9E\x9F] )
          [^\x1B\x9C]*
          (?: \x1B\\ | \x9C )
        | (?: \x1B\[ | \x9B ) [0-?]* [ -/]* [@-~]   # CSI
        | \x1B [@-Z\\-_]                            # other 7-bit Fe sequences
        | [\x80-\x9A\x9C-\x9F]                      # bare 8-bit C1 controls
          # Plain ESC sequences. The final bytes are listed instead of taken
          # from a range: ECMA-35 allows any of [0-~] there, which would eat
          # the character after a stray ESC in otherwise plain text.
        | \x1B [!-/]+ [0-~]                         # nF: ESC ( B, ESC # 8
        | \x1B [78=>]                               # Fp: DECSC/DECRC, keypad
        | \x1B [clmno|}~]                           # Fs: RIS, locking shifts
    )""",
    re.VERBOSE,
)


def ansi_strip(text: str) -> str:
    """
    Remove ANSI escape/control sequences from a string.

    :param text: str: Text.
    :return: str: The text without ANSI escape/control sequences.

    """
    return ansi_escape.sub("", text)
