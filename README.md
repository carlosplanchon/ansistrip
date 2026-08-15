# Ansistrip

![ansistrip banner](https://raw.githubusercontent.com/carlosplanchon/ansistrip/master/assets/banner.jpg)

*Mini-lib to strip ANSI Escape codes from a string.*

[![CI](https://github.com/carlosplanchon/ansistrip/actions/workflows/ci.yml/badge.svg)](https://github.com/carlosplanchon/ansistrip/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ansistrip.svg)](https://pypi.org/project/ansistrip/)
[![Python versions](https://img.shields.io/pypi/pyversions/ansistrip.svg)](https://pypi.org/project/ansistrip/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/carlosplanchon/ansistrip)

## Installation
### Install with uv:
```
uv add ansistrip
```

## Usage
```
In [1]: import ansistrip

In [2]: text = "\x1b[1m\x1b[38;5;10mtest\x1b[0m"

In [3]: ansistrip.ansi_strip(text)
Out[3]: 'test'
```

It also handles 8-bit C1 controls, plain ESC sequences such as `ESC ( B` or
`ESC c`, and control strings such as terminal titles and OSC 8 hyperlinks:
```
In [4]: ansistrip.ansi_strip("\x1b]0;my title\x07hello")
Out[4]: 'hello'

In [5]: ansistrip.ansi_strip("\x1b]8;;https://example.com\x1b\\link\x1b]8;;\x1b\\")
Out[5]: 'link'
```

Non-ASCII text is left untouched:
```
In [6]: ansistrip.ansi_strip("\x1b[31mÉXITO: configuración\x1b[0m")
Out[6]: 'ÉXITO: configuración'
```

## Development
```
uv sync
uv run pytest
```
