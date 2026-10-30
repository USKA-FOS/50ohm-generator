from pathlib import Path

import pytest
from mistletoe import Document

from renderer.formula_layout import classify, display_html, math_spans
from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


@pytest.mark.parametrize('text,language,layout', [
    (r'$U=RI$', 'de', 'block'),
    (r'$U=RI$.', 'de', 'block'),
    (r'$U=RI$ oder $I=U/R$', 'de', 'block'),
    (r'$U=RI$ ou $I=U/R$.', 'fr', 'block'),
    (r'$U=RI$ oppure $I=U/R$', 'it', 'block'),
    (r'La tension vaut $U=RI$.', 'fr', 'inline'),
    (r'$U=RI$ unknown $I=U/R$', 'de', 'preserve'),
    (r'$U=RI$ oder $I=U/R$', 'fr', 'preserve'),
    (r'Price \$5, tension $U$.', 'de', 'inline'),
    (r'$U_{eff} = \frac{\hat{U}}{\sqrt{2}}$ oder $\hat{U} = U_{eff} \cdot \sqrt{2}$', 'de', 'block'),
    (r'$\hat{U}=\qty{230}{\volt}\sqrt{2}\approx\qty{325}{\volt}$.', 'de', 'block'),
])
def test_layout_policy(text, language, layout):
    assert classify(text, language)['layout'] == layout


def test_scanner_handles_escaped_dollars_and_nested_groups():
    spans, malformed = math_spans(r'Price \$5: $x_{a_{b}}+\text{\$}$.')
    assert not malformed
    assert [s.body for s in spans] == [r'x_{a_{b}}+\text{\$}']
    assert classify('$x_{a$')['ambiguous']


def test_promotion_preserves_math_bodies_connector_and_punctuation():
    source = r'$U_{eff}=\frac{\hat U}{\sqrt2}$ oder $\hat U=U_{eff}\sqrt2$.'
    classification = classify(source)
    output = display_html(source, classification)
    assert [s.body for s in math_spans(output)[0]] == classification['bodies']
    assert '</span> oder <span' in output
    assert output.endswith('.</span></div>\n')


def test_question_answer_and_html_are_not_implicitly_promoted():
    assert classify('$U=RI$', context='answer')['layout'] == 'inline'
    assert classify('<em>$U=RI$</em>')['layout'] == 'preserve'


def test_complete_multiline_paragraph_is_not_mistaken_for_block():
    with FiftyOhmHtmlRenderer() as renderer:
        result = renderer.render(Document('$U=RI$.\nThis is still the same paragraph.'))
    assert 'formula-block' not in result


def test_rendering_matches_policy_and_slides_keep_old_layout():
    source = '$U=RI$ oder $I=U/R$'
    with FiftyOhmHtmlRenderer() as renderer:
        assert 'formula-block' in renderer.render(Document(source))
    with FiftyOhmHtmlSlideRenderer() as renderer:
        assert 'formula-block' not in renderer.render(Document(source))


def test_bare_formula_remains_legacy_in_opted_out_renderer():
    with FiftyOhmHtmlRenderer(formula_layout=False) as renderer:
        assert '$$U=RI$$' in renderer.render(Document('$U=RI$'))


def test_malformed_legacy_formula_does_not_abort_html_rendering():
    with FiftyOhmHtmlRenderer() as renderer:
        result = renderer.render(Document('$U_{$'))
    assert '$$U_{$$' in result
    assert 'formula-block' not in result


@pytest.mark.parametrize('language,connector', [('de', 'oder'), ('fr', 'ou'), ('it', 'oppure')])
def test_real_generator_template_integrates_contextual_assets(tmp_path, language, connector):
    import json
    from types import SimpleNamespace
    from src.build import Build

    generator = Path(__file__).resolve().parents[1]
    extras = tmp_path/'extra'
    for lang in ('de', 'fr', 'it'):
        folder = extras/lang
        (folder/'templates/html').mkdir(parents=True)
        (folder/'labels.json').write_text(json.dumps({'html_lang': lang}))
        (folder/'templates/html/header-language-controls.html').write_text(
            '{% macro beta_control() %}{% endmacro %}'
            '{% macro language_controls() %}{% endmacro %}')
    # Only the four assets exercised here are needed. Avoid copying the entire
    # vendored Reveal/font tree for each locale in temporary test output.
    import shutil
    source_assets = tmp_path/'source-assets'
    source_assets.mkdir()
    for name in ('style-course.css', 'formula-inline.js', 'latex.js', 'script.js'):
        shutil.copy2(generator/'assets'/name, source_assets/name)
    catalog = tmp_path/'catalog.json'
    catalog.write_text('{"sections": []}')
    config = SimpleNamespace(
        random_seed=50, language=language, release_id=None, beta=False,
        feedback_url=None, review_workflow=False,
        p_generator_extra_content_default=extras/'de',
        p_generator_extra_content_language=extras/language,
        p_templates=generator/'templates', p_assets=source_assets,
        p_data_fragenkatalog=catalog, p_data_fragenkatalog_upstream=None,
        p_build=tmp_path/'build', p_build_assets=tmp_path/'build/assets',
        shuffle_answers=False,
    )
    builder = Build(config)
    with FiftyOhmHtmlRenderer(ui_labels=builder.ui_labels) as renderer:
        content = renderer.render(Document(f'$U=RI$ {connector} $I=U/R$'))
    page = builder.env.get_template('html/page.html').render(
        content=content, course_wrapper=True, sidebar=None)
    builder.build_assets()
    assert f'<html lang="{language}" data-formula-presentation="contextual">' in page
    assert 'data-formula-rule="connected_formula_group"' in page
    for asset, version in (('style-course.css', 'formula-layout-2'),
                           ('formula-inline.js', 'formula-layout-1'),
                           ('latex.js', 'formula-layout-1')):
        assert f'assets/{asset}?v={version}' in page
        assert (config.p_build_assets/asset).is_file()
    assert page.index('assets/formula-inline.js') < page.index('assets/latex.js')
