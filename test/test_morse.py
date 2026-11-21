import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


@pytest.mark.html
def test_morse_html():
    assertions = {
        "[morse:a]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]], playable=True),
        "[morse:a] abc [morse:a]": f"{FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]], playable=True)} abc {FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]], playable=True)}",  # noqa: E501
        "[morse: a]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]], playable=True),
        "[morse: aaa]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2], [1, 2], [1, 2]], playable=True),
        "[morse: a a]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2], [3], [1, 2]], playable=True),
        "[morse: db0]": FiftyOhmHtmlRenderer.render_morse_helper(
            [[2, 1, 1], [2, 1, 1, 1], [2, 2, 2, 2, 2]], playable=True
        ),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


@pytest.mark.html
def test_morse_html_playable_markup():
    html = mistletoe.markdown("[morse: cq cq]", FiftyOhmHtmlRenderer)
    assert 'class="morse morse-playable"' in html
    assert 'data-morse="2121 2212 3 2121 2212"' in html
    assert 'role="button"' in html
    assert 'tabindex="0"' in html


@pytest.mark.html
def test_morse_html_prosign_encoding():
    html = mistletoe.markdown("[morse:sk]", FiftyOhmHtmlRenderer)
    assert 'data-morse="111212"' in html


@pytest.mark.html
def test_morse_slides_not_playable():
    from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer

    html = mistletoe.markdown("[morse:a]", FiftyOhmHtmlSlideRenderer)
    assert "morse-playable" not in html
    assert "data-morse" not in html
    assert '<span class="morse">' in html
