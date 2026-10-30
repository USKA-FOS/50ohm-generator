import json
from pathlib import Path

import pytest

from tools.audit_formula_layout import Paragraphs, scan
from renderer.formula_layout import classify


def extract(source):
    parser = Paragraphs()
    parser.feed(source)
    parser.close()
    return parser


def test_raw_display_entities_are_one_complete_node():
    parser = extract(r'<div class="course">$$\begin{align*}g &amp;= 10\\ x &gt; 1\end{align*}$$</div>')
    assert len(parser.fragments) == 1
    result = classify(parser.fragments[0]['fragment'])
    assert result['layout'] == 'block'
    assert result['rule'] != 'unbalanced_delimiters'
    assert result['formula_count'] == 1


@pytest.mark.parametrize('tag', ['script', 'style', 'noscript', 'code', 'pre', 'textarea', 'option'])
def test_non_math_elements_do_not_leak_dollars(tag):
    source = f'<div class="course"><{tag}>${{javascript}}</{tag}><p>Voltage $U$.</p></div>'
    parser = extract(source)
    assert len(parser.fragments) == 1
    assert parser.fragments[0]['fragment'] == 'Voltage $U$.'
    assert parser.ignored_elements[tag] == 1


def test_math_in_list_items_coalesces_named_and_numeric_entities():
    parser = extract('<div class="course"><li>Bei $f&lt;f_0$.</li><li>$x&#62;y$</li></div>')
    assert len(parser.fragments) == 2
    assert all(not classify(b['fragment'])['ambiguous'] for b in parser.fragments)
    assert parser.fragments[0]['fragment'] == 'Bei $f&lt;f_0$.'


def test_adjacent_text_is_flushed_on_actual_markup_boundaries():
    parser = extract('<div class="course">$x<span>middle</span>y$</div>')
    assert len(parser.fragments) == 2
    assert all(classify(b['fragment'])['rule'] == 'unbalanced_delimiters' for b in parser.fragments)


def test_mixed_code_paragraph_keeps_code_in_preview_but_not_in_analysis():
    parser = extract('<div class="course"><p>Value $U$, code <code>$unclosed</code>.</p></div>')
    block = parser.fragments[0]
    assert '<code>$unclosed</code>' in block['fragment']
    assert '$unclosed' not in block['analysis_fragment']
    assert classify(block['analysis_fragment'])['rule'] != 'unbalanced_delimiters'


def test_genuinely_unbalanced_math_remains_flagged():
    parser = extract('<div class="course"><p>Voltage $U.</p></div>')
    assert classify(parser.fragments[0]['analysis_fragment'])['rule'] == 'unbalanced_delimiters'


def test_inventory_preserves_pages_and_records_exclusions(tmp_path, capsys):
    site = tmp_path/'site'
    (site/'de').mkdir(parents=True)
    (site/'de/page.html').write_text('<div class="course"><script>$("#x")</script>$$x &amp;= y$$</div>')
    report = tmp_path/'report.json'
    scan(site, report)
    data = json.loads(report.read_text())
    assert data['summary']['rules'].get('unbalanced_delimiters', 0) == 0
    assert data['summary']['unique_items'] == 1
    assert data['extraction']['ignored_elements'] == {'script': 1}
    assert data['source_sha256']['de/page.html']


def test_before_preview_uses_explicit_frozen_assets(tmp_path):
    from tools.audit_formula_layout import preview

    frozen = tmp_path/'frozen'
    frozen.mkdir()
    for name in ('katex', 'font'):
        (frozen/name).mkdir()
        (frozen/name/'historical.txt').write_text('historical '+name)
    for name in ('latex.js', 'style-course.css', 'style-fiftyohm.css', 'hb_beta.css'):
        (frozen/name).write_text('historical '+name)
    report = tmp_path/'report.json'
    report.write_text(json.dumps({'items': []}))
    output = tmp_path/'before'
    preview(report, output, 'before', assets_from=frozen)
    assert (output/'assets/style-course.css').read_text() == 'historical style-course.css'
    assert not (output/'assets/formula-inline.js').exists()
    assert 'data-formula-presentation="contextual"' not in (output/'index.html').read_text()
