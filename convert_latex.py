import re

_PATTERN = re.compile(
    r'(?P<math>\$\$[^$]*\$\$|\$[^$]*\$)'                                           # $$...$$ or $...$ – pass through intact
    r'|(?P<comma>\{,\})'                                                            # {,}
    r'|(?P<tilde>~)'                                                                # ~
    r'|\\underline\{(?P<ul_body>(?:[^{}]|\{[^{}]*\})*)\}'                         # \underline{...}
    r'|\\glqq (?P<glqq_body>.*?)\\grqq(?:\{\}| )'                                 # \glqq...\grqq
    r'|(?P<num>\\num\{[^}]*\})'                                                    # \num{...}
    r'|\\qty(?:\[.*?\])?\{(?P<qty_val>[^}]*)\}\{(?P<qty_unit>[^}]*)\}'            # \qty[opt]{val}{unit}
    r'|\\qtyrange(?:\[.*?\])?\{(?P<qr_v1>[^}]*)\}\{(?P<qr_v2>[^}]*)\}\{(?P<qr_unit>[^}]*)\}'  # \qtyrange[opt]{}{}{unit}
)


def _replace(m: re.Match) -> str:
    if m.group('math') is not None:
        return m.group(0)
    if m.group('comma') is not None:
        return ','
    if m.group('tilde') is not None:
        return '&#8239;'
    if m.group('ul_body') is not None:
        return f'<u>{_PATTERN.sub(_replace, m.group("ul_body"))}</u>'
    if m.group('glqq_body') is not None:
        return f'«{m.group("glqq_body")}»'
    if m.group('num') is not None:
        return f'${m.group(0)}$'
    if m.group('qty_val') is not None:
        return f'$\\qty{{{m.group("qty_val")}}}{{{m.group("qty_unit")}}}$'
    if m.group('qr_v1') is not None:
        return f'$\\qtyrange{{{m.group("qr_v1")}}}{{{m.group("qr_v2")}}}{{{m.group("qr_unit")}}}$'
    return m.group(0)  # unreachable


def convert_latex(s: str) -> str:
    return _PATTERN.sub(_replace, s)
