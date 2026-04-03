import re
from mistletoe.span_token import SpanToken


class Tilde(SpanToken):
    """
    Identifies Tilde (~)
    """
    pattern = re.compile(r"~")
    parse_group = 0  # standalone token


class GLDoubleQuotes(SpanToken):
    """
    Identifies German Left Double Quote (\\glqq) and German Right Double Quote (\\grqq{})
    """
    pattern = re.compile(r"\\glqq (.*?)\\grqq(?:\{\}| )")


class Math(SpanToken):
    """
    Identifies math ($...$).
    We prevent innert parsing. By not parsing inside math, the solution to surround \\qty
    by $$ will not apply and we have a clean \\qty without surrounding $...$ inside math.
    """
    pattern = re.compile(r'\$.+?\$')
    parse_inner = False
    parse_group = 0  # standalone token


class MathComma(SpanToken):
    """
    Identifies {,}, used e.g. in 0{,}707
    """
    pattern = re.compile(r"\{,\}")
    parse_group = 0  # standalone token


class Num(SpanToken):
    """
    Identifies \\num{...}
    """
    pattern = re.compile(r"(\\num\{[^}]*\})")
    parse_inner = False


class Qty(SpanToken):
    """
    Identifies \\qty[...]{...}{...}
    """
    pattern = re.compile(r'\\qty(\[.*?\])?\{(?P<value>.*?)\}\{(?P<unit>.*?)\}')
    parse_inner = False

    def __init__(self, match):
        super().__init__(match)
        self.value = match.group('value')
        self.unit = match.group('unit')


class Qtyrange(SpanToken):
    """
    Identifies \\qtyrange[...]{...}{...}{...}
    """
    pattern = re.compile(r'\\qtyrange(\[.*?\])?\{(?P<value1>.*?)\}\{(?P<value2>.*?)\}\{(?P<unit>.*?)\}')
    parse_inner = False

    def __init__(self, match):
        super().__init__(match)
        self.value1 = match.group('value1')
        self.value2 = match.group('value2')
        self.unit = match.group('unit')


class Underline(SpanToken):
    """
    Identifies underlined text (\\underline{...})
    """
    pattern = re.compile(r"\\underline\{(.*?)\}")
