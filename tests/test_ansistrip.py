#!/usr/bin/env python3

import pytest

from ansistrip import ansi_strip


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Plain text is left untouched.
        ("", ""),
        ("hello world", "hello world"),
        # SGR sequences.
        ("\x1b[1m\x1b[38;5;10mtest\x1b[0m", "test"),
        ("\x1b[31mred\x1b[0m and \x1b[32mgreen\x1b[0m", "red and green"),
        # Non-SGR CSI sequences: cursor movement, erase.
        ("x\x1b[2Ay", "xy"),
        ("\x1b[2J\x1b[Hcleared", "cleared"),
        # 8-bit C1 controls: CSI (0x9B) and a bare one (IND, 0x84).
        ("a\x9b31mb", "ab"),
        ("a\x84b", "ab"),
        # Other 7-bit Fe sequences.
        ("a\x1bEb", "ab"),
        # OSC with a BEL terminator: terminal title.
        ("\x1b]0;my title\x07hello", "hello"),
        # OSC 8 hyperlinks, terminated by ST.
        ("\x1b]8;;http://a.com\x1b\\text\x1b]8;;\x1b\\", "text"),
        # DCS.
        ("\x1bPsomething\x1b\\ok", "ok"),
    ],
)
def test_ansi_strip(text: str, expected: str) -> None:
    assert ansi_strip(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # BEL only terminates OSC. Inside DCS, SOS, PM and APC it is just
        # payload, so those run until the ST.
        ("\x1bPfoo\x07bar\x1b\\", ""),
        ("\x1bXsos\x07str\x1b\\", ""),
        ("\x1b^priv\x07ate\x1b\\", ""),
        ("\x1b_data\x07more\x1b\\", ""),
        ("\x1bPq#0;2;0;0;0\x1b\\ok", "ok"),
        # 8-bit introducers and 8-bit ST (0x9C).
        ("\x90dcs\x07payload\x9cok", "ok"),
        # OSC keeps taking either terminator.
        ("\x1b]0;title\x07hello", "hello"),
        ("\x1b]0;title\x1b\\hello", "hello"),
        ("\x9d0;title\x07hello", "hello"),
    ],
)
def test_control_string_terminators(text: str, expected: str) -> None:
    """Only OSC ends at a BEL; the other control strings need an ST."""
    assert ansi_strip(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "ÉXITO: configuración cargada",
        "ÀÉÍÓÚ",
        "日本語",
        "🎉 emoji 🎨",
        "€ ñandú",
    ],
)
def test_non_ascii_is_preserved(text: str) -> None:
    """The old bytes-mode regex ate UTF-8 continuation bytes and raised."""
    assert ansi_strip(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("\x1b[31mÉXITO\x1b[0m", "ÉXITO"),
        ("\x1b[1m日本語\x1b[0m", "日本語"),
        ("\x1b]0;título\x07configuración", "configuración"),
    ],
)
def test_non_ascii_with_ansi(text: str, expected: str) -> None:
    assert ansi_strip(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Fs: RIS, memory lock/unlock, locking shifts.
        ("a\x1bcb", "ab"),
        ("a\x1blb", "ab"),
        ("a\x1bmb", "ab"),
        ("a\x1bnb", "ab"),
        ("a\x1bob", "ab"),
        ("a\x1b|b", "ab"),
        ("a\x1b}b", "ab"),
        ("a\x1b~b", "ab"),
        # Fp: save/restore cursor and keypad modes.
        ("a\x1b7b", "ab"),
        ("a\x1b8b", "ab"),
        ("a\x1b=b", "ab"),
        ("a\x1b>b", "ab"),
        # nF: character set designation and friends.
        ("a\x1b(Bb", "ab"),
        ("a\x1b)0b", "ab"),
        ("a\x1b#8b", "ab"),
        ("a\x1b%Gb", "ab"),
        ("\x1b(B\x1b[mok", "ok"),
    ],
)
def test_plain_escape_sequences(text: str, expected: str) -> None:
    assert ansi_strip(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # A lone ESC at the end of the string is not a sequence.
        ("end\x1b", "end\x1b"),
        # An unterminated control string only loses its introducer.
        ("\x1b]0;broken", "0;broken"),
        # A stray ESC must not swallow the character that follows it. This is
        # why the plain-ESC branch lists its final bytes one by one.
        ("presione \x1b para salir", "presione \x1b para salir"),
        ("\x1bfin", "\x1bfin"),
        ("a\x1bzb", "a\x1bzb"),
    ],
)
def test_incomplete_sequences(text: str, expected: str) -> None:
    assert ansi_strip(text) == expected


def test_is_idempotent() -> None:
    text = "\x1b[1m\x1b[38;5;10mtest\x1b[0m con acentuación"
    once = ansi_strip(text)
    assert ansi_strip(once) == once
