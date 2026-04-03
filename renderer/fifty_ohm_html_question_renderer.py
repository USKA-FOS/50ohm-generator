from .fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from .question_markup import GLDoubleQuotes, Math, MathComma, Num, Qty, Qtyrange, Tilde, Underline


class FiftyOhmHtmlQuestionRenderer(FiftyOhmHtmlRenderer):
    def __init__(self, *extras, **kwargs):
        super().__init__(
            GLDoubleQuotes,
            Math,        # Must come before Qty
            MathComma,
            Num,
            Qty,
            Qtyrange,
            Tilde,
            Underline,
            *extras,
            **kwargs,
        )

    def render_paragraph(self, token):
        return self.render_inner(token)  # removes <p> wrapper

    def render_gl_double_quotes(self, token):
        return '„' + self.render_inner(token) + '“'
        return '«' + self.render_inner(token) + '»'  # FIXME: This is even more Swiss

    def render_math(self, token):
        return token.content

    def render_math_comma(self, token):
        return ','

    def render_num(self, token):
        return f'${token.content}$'

    def render_qty(self, token):
        return '$\\qty{' + token.value + '}{' + token.unit + '}$'
        return f'${token.content}$'

    def render_qtyrange(self, token):
        return '$\\qtyrange{' + token.value1 + '}{' + token.value2 + '}{' + token.unit + '}$'
        return f'${token.content}$'

    def render_tilde(self, token):
        return '&#8239;'
        return '&nbsp;'

    def render_underline(self, token):
        return '<u>' + self.render_inner(token) + '</u>'

    def render_formula(self, token):
        # Overriding FiftyOhmHtmlRenderer which wants to turn this into a block
        return f"${token.formula}$"
