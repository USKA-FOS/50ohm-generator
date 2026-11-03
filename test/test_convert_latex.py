"""Regression checks for the question text conversion shared by HTML and slides."""
import pytest

from convert_latex import convert_latex


@pytest.mark.parametrize('source,expected', [
    (r'Was ist die mit \glqq?\grqq{} bezeichnete Stufe?',
     'Was ist die mit „?“ bezeichnete Stufe?'),
    (r'\glqq TEXT\grqq{}', '„TEXT“'),
    (r'\glqq{}TEXT\grqq{}', '„TEXT“'),
    (r'\glqq?\grqq.', '„?“.') ,
    (r'\glqq!\grqq', '„!“'),
    (r'\glqq TEXT\grqq weiter', '„TEXT“weiter'),
    (r'\glqq?\grqq{} und \glqq!\grqq{}', '„?“ und „!“'),
])
def test_tex_quotation_command_delimiters(source, expected):
    assert convert_latex(source) == expected


@pytest.mark.parametrize('source', [
    r'\glqqTEXT\grqq{}',
    r'\glqq TEXT\grqqOther{}',
    r'\glqq ohne Abschluss',
    r'$\glqq?\grqq{}$',
    r'$$\glqq?\grqq{}$$',
])
def test_do_not_convert_other_commands_incomplete_quotes_or_math(source):
    assert convert_latex(source) == source


def test_existing_question_conversions_are_preserved():
    assert convert_latex(r'\glqq?\grqq{} bei \qty{230}{\volt}') == r'„?“ bei $\qty{230}{\volt}$'
    assert convert_latex(r'\underline{\glqq?\grqq{}}') == '<u>„?“</u>'
