#!/usr/bin/env python
"""Read-only release inventory and frozen before/after formula preview builder."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from renderer.formula_layout import classify, display_html, math_spans


class Paragraphs(HTMLParser):
    """Collect complete visible text nodes, not individual parser callbacks.

    HTMLParser splits text at entity references even though the browser does
    not. Keep those callbacks together, and exclude the same non-math elements
    as KaTeX auto-render. Paragraph HTML is retained for the diagnostic preview;
    code contents are omitted only from the classification input.
    """
    IGNORED = {"script", "style", "noscript", "pre", "code", "textarea", "option"}
    HIDDEN = {"script", "style", "noscript"}
    VOID = {"img", "br", "hr", "meta", "link", "input", "source", "wbr",
            "area", "base", "embed", "param", "track", "col"}

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.active = None
        self.fragments = []
        self.raw_parts = []
        self.raw_line = None
        self.ignored_elements = Counter()

    def ignored(self):
        return any(tag in self.IGNORED for tag, _ in self.stack)

    def hidden(self):
        return any(tag in self.HIDDEN for tag, _ in self.stack)

    def flush_raw(self):
        if self.raw_parts:
            text = ''.join(self.raw_parts)
            stripped = text.strip()
            if '$' in stripped or r"\(" in stripped or r"\[" in stripped:
                leading = text[:len(text) - len(text.lstrip())]
                self.fragments.append({
                    'fragment': html.escape(stripped, quote=False),
                    'context': 'prose', 'line': self.raw_line + leading.count('\n'),
                    'raw_display': True,
                })
        self.raw_parts = []
        self.raw_line = None

    def handle_starttag(self, tag, attrs):
        self.flush_raw()
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        in_course = any('course' in frame[1] for frame in self.stack)
        ignored = self.ignored()
        if tag in self.IGNORED and in_course:
            self.ignored_elements[tag] += 1
        if self.active is not None:
            if tag not in self.HIDDEN and not self.hidden():
                self.active['parts'].append(self.get_starttag_text())
            if not ignored and tag not in self.IGNORED:
                self.active['analysis_parts'].append(self.get_starttag_text())
            elif not ignored and tag not in self.HIDDEN:
                self.active['analysis_parts'].append(f'<{tag}></{tag}>')
        elif not ignored and tag not in self.IGNORED and in_course and (
                tag == 'p' or 'question-text' in classes or
                tag == 'button' and any('answers' in f[1] for f in self.stack)):
            context = 'answer' if tag == 'button' else 'question' if 'question-text' in classes else 'prose'
            self.active = {'depth': len(self.stack), 'context': context, 'parts': [],
                           'analysis_parts': [], 'line': self.getpos()[0]}
        if tag not in self.VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        self.flush_raw()
        if self.active is not None:
            if len(self.stack) == self.active['depth'] + 1 and self.stack[-1][0] == tag:
                self.active['fragment'] = ''.join(self.active.pop('parts')).strip()
                self.active['analysis_fragment'] = ''.join(self.active.pop('analysis_parts')).strip()
                self.fragments.append(self.active)
                self.active = None
            else:
                if not self.hidden() and tag not in self.HIDDEN:
                    self.active['parts'].append(f'</{tag}>')
                if not self.ignored():
                    self.active['analysis_parts'].append(f'</{tag}>')
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.active is not None:
            if not self.hidden():
                self.active['parts'].append(html.escape(data, quote=False))
            if not self.ignored():
                self.active['analysis_parts'].append(html.escape(data, quote=False))
        elif not self.ignored() and any('course' in f[1] for f in self.stack):
            if self.raw_line is None:
                self.raw_line = self.getpos()[0]
            self.raw_parts.append(data)

    def handle_entityref(self, name):
        self.handle_data(html.unescape('&' + name + ';'))

    def handle_charref(self, name):
        self.handle_data(html.unescape('&#' + name + ';'))

    def handle_comment(self, data):
        self.flush_raw()

    def close(self):
        super().close()
        self.flush_raw()


def variant(fragment, classification, context):
    flags = [name for name, pattern in {
        'fraction': r'\\(?:d?frac)', 'accent': r'\\(?:hat|bar|vec|dot)',
        'index': r'_', 'unit': r'\\(?:qty|unit|num)',
        'greek': r'\\(?:alpha|beta|gamma|omega|Omega|pi|mu|lambda|phi)',
        'explicit_font': r'\\(?:mathrm|textrm|mathsf|symup|text|mathbf)',
    }.items() if re.search(pattern, fragment)]
    return '|'.join([context, classification['rule'], '+'.join(flags) or 'simple'])


def scan(site, output):
    items = {}
    fingerprints = {}
    pages = 0
    ignored_elements = Counter()
    for language_root in sorted(site.iterdir()):
        language = language_root.name
        if language not in ('de', 'fr', 'it'):
            continue
        for path in sorted(language_root.glob('*.html')):
            raw = path.read_bytes()
            relative = path.relative_to(site).as_posix()
            fingerprints[relative] = hashlib.sha256(raw).hexdigest()
            parser = Paragraphs()
            parser.feed(raw.decode('utf-8'))
            parser.close()
            ignored_elements.update(parser.ignored_elements)
            pages += 1
            for block in parser.fragments:
                fragment = block['fragment']
                analysis_fragment = block.get('analysis_fragment', fragment)
                result = classify(analysis_fragment, language, context=block['context'])
                if result['rule'] == 'no_math':
                    continue
                ident = hashlib.sha256((language+'\0'+block['context']+'\0'+fragment).encode()).hexdigest()[:16]
                if ident not in items:
                    spans, _ = math_spans(analysis_fragment)
                    items[ident] = {'id': ident, 'language': language,
                        'context': block['context'], 'fragment': fragment, 'analysis_fragment': analysis_fragment,
                        'classification': result,
                        'variant': variant(fragment, result, block['context']),
                        'current_display': any(s.display for s in spans),
                        'locations': []}
                items[ident]['locations'].append({'page': relative, 'line': block['line']})
    records = list(items.values())
    report = {'schema_version': 1, 'site_root': str(site.resolve()),
        'config_sha256': hashlib.sha256((ROOT/'config/formula-layout.json').read_bytes()).hexdigest(),
        'pages_scanned': pages, 'source_sha256': fingerprints,
        'extraction': {'coalesced_text_nodes': True, 'ignored_elements': dict(ignored_elements)},
        'summary': {'unique_items': len(records), 'occurrences': sum(len(i['locations']) for i in records),
                    'rules': dict(Counter(i['classification']['rule'] for i in records)),
                    'variants': len({i['variant'] for i in records}),
                    'promotions': sum(i['context']=='prose' and i['classification']['layout']=='block' and not i['current_display'] for i in records),
                    'ambiguous': sum(i['classification']['ambiguous'] for i in records)},
        'items': records}
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit('Refusing to replace existing report: '+str(output))
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    output.with_suffix('.md').write_text('# Formula layout inventory\n\n'+
        '\n'.join(f'- {key}: {value}' for key, value in report['summary'].items())+
        '\n\nOnly detected complete prose paragraphs are eligible for promotion. '
        'Question/answer fields, markup and ambiguous separators are preserved.\n')
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))


def preview(report_path, output, phase, *, assets_from=None):
    report = json.loads(report_path.read_text())
    if output.exists():
        raise SystemExit('Refusing to overwrite a preview: '+str(output))
    output.mkdir(parents=True)
    assets = output/'assets'
    assets.mkdir()
    for name in ('katex', 'latex.js', 'style-course.css', 'style-fiftyohm.css', 'hb_beta.css', 'font') + (('formula-inline.js',) if phase == 'after' else ()):
        source = (ROOT/'assets' if assets_from is None else assets_from)/name
        if source.is_dir():
            shutil.copytree(source, assets/name)
        else:
            shutil.copy2(source, assets/name)
    groups = {}
    for item in report['items']:
        groups.setdefault(item['variant'], []).append(item)
    selected = {}
    for group in groups.values():
        for item in group[:2]:
            selected[item['id']] = item
    # Always include every mathematical fragment from the reported example page.
    for item in report['items']:
        if any(loc['page']=='de/NE_spitze_effektiv_wert.html' for loc in item['locations']):
            selected[item['id']] = item
    articles = []
    ordered = sorted(selected.values(), key=lambda item: not any(loc['page']=='de/NE_spitze_effektiv_wert.html' for loc in item['locations']))
    for item in ordered:
        fragment = item['fragment']
        classification = item['classification']
        if phase == 'after' and item['context']=='prose' and classification['layout']=='block':
            rendered = display_html(fragment, classification)
        elif item['current_display']:
            rendered = fragment
        else:
            rendered = '<p>'+fragment+'</p>'
        if item['context']=='question':
            rendered = '<div class="question-text">'+fragment+'</div>'
        elif item['context']=='answer':
            # Omit production answer widgets and keep the exact text/math.
            rendered = '<div class="question"><div class="answers"><button>'+fragment+'</button></div></div>'
        where = item['locations'][0]
        label = f"{item['language']} — {item['variant']} — {where['page']}:{where['line']}"
        articles.append('<article id="case-'+item['id']+'"><h2>'+html.escape(label)+
            '</h2><p class="meta">'+html.escape(str(len(item['locations']))+' occurrences; current: '+('display' if item['current_display'] else 'inline')+'; proposed: '+classification['layout'])+
            '</p><div class="course" lang="'+item['language']+'">'+rendered+'</div><details><summary>HTML source</summary><pre>'+html.escape(fragment)+'</pre></details></article>')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Formula presentation — '''+phase+'''</title>
<link rel="stylesheet" href="assets/style-fiftyohm.css"><link rel="stylesheet" href="assets/style-course.css"><link rel="stylesheet" href="assets/katex/katex.min.css"><link rel="stylesheet" href="assets/hb_beta.css">
<style>body{display:block;box-sizing:border-box;height:auto;max-width:1000px;margin:auto;padding:1rem}article{border:1px solid #ccc;padding:1rem;margin:1rem 0}h2{font-size:1rem;overflow-wrap:anywhere}.meta{color:#555;font-size:.8rem}.course{padding:1rem;box-sizing:border-box;min-width:0;max-width:100%}.course .question{width:100%}pre{white-space:pre-wrap}details{margin-top:1rem}</style>
<script defer src="assets/katex/katex.min.js"></script><script defer src="assets/katex/auto-render.min.js"></script><script defer src="assets/formula-inline.js"></script><script defer src="assets/latex.js"></script></head><body><h1>Formula presentation — '''+phase+'''</h1><p>Same frozen source inventory. Representative cases for every observed variant; full affected page included. No canonical edits.</p>'''+''.join(articles)+'</body></html>'
    if phase == 'after':
        page = page.replace('<html lang="en">', '<html lang="en" data-formula-presentation="contextual">')
    else:
        page = page.replace('<script defer src="assets/formula-inline.js"></script>', '')
    metrics_script = """<script>
window.addEventListener('load', function () {
  requestAnimationFrame(function () {
    const samples = [...document.querySelectorAll('article')].map(article => {
      const formulas = [...article.querySelectorAll('.course .katex')].map(el => ({
        display: !!el.closest('.katex-display'),
        fontSize: getComputedStyle(el).fontSize,
        parentFontSize: getComputedStyle(el.parentElement).fontSize,
        variableFont: el.querySelector('.mathnormal,.textsf.textit') ?
          getComputedStyle(el.querySelector('.mathnormal,.textsf.textit')).fontFamily : null
      }));
      return {id:article.id, errors:article.querySelectorAll('.katex-error').length, formulas};
    });
    const data = document.createElement('script'); data.type='application/json';
    data.id='formula-browser-metrics'; data.textContent=JSON.stringify(samples);
    document.body.appendChild(data);
  });
});
</script>"""
    selection_script = "<script>function selectCase(){const id=location.hash.slice(1);document.querySelectorAll('article').forEach(a=>{a.hidden=!!id&&a.id!==id;});}window.addEventListener('hashchange',selectCase);selectCase();</script>"
    page = page.replace('</body>', metrics_script + selection_script + '</body>')
    (output/'index.html').write_text(page)
    audit = {'phase':phase,'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),
             'samples':len(selected),'variants':len(groups),'selected_ids':list(selected),
             'assets_sha256':{p.relative_to(assets).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(assets.rglob('*')) if p.is_file()}}
    (output/'preview-manifest.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(f'{phase}: {len(selected)} samples, {len(groups)} variants, {output}/index.html')



def compare(report_path, before, after, output):
    report = json.loads(report_path.read_text())
    first = json.loads((before/'preview-manifest.json').read_text())
    second = json.loads((after/'preview-manifest.json').read_text())
    assert first['report_sha256'] == second['report_sha256']
    assert set(first['selected_ids']) == set(second['selected_ids'])
    groups = {}
    for item in report['items']:
        groups.setdefault(item['variant'], item)
    chosen = next((i for i in report['items'] if i['language']=='de' and 'U_{eff} = ' in i['fragment']), next(iter(groups.values())))
    options = ''.join('<option value="case-'+i['id']+'">'+html.escape(v)+'</option>' for v,i in groups.items())
    options += '<option value="case-'+chosen['id']+'" selected>Exemple demandé — Ueff / Û</option>'
    b = os.path.relpath(before/'index.html', output.parent)
    a = os.path.relpath(after/'index.html', output.parent)
    page = """<!doctype html><html lang="fr"><meta charset="utf-8"><title>Validation des formules</title>
<style>body{font-family:Arial,sans-serif;margin:1rem;color:#222}h1{font-size:1.6rem}select{width:95%;padding:.5rem}.panels{display:block;width:100%}.panels>section[hidden]{display:none}.view-controls{display:flex;gap:.5rem;margin:1rem 0}.view-controls button{padding:.5rem 1rem}.view-controls button[aria-pressed="true"]{background:#ac2d24;color:white;border:1px solid #ac2d24}iframe{width:100%;height:75vh;border:1px solid #aaa}h2{font-size:1.2rem}a{color:#ac2d24}@media(max-width:900px){.panels{grid-template-columns:1fr}}</style>
<h1>Validation du rendu des formules — avant / après</h1><p>Inventaire de {pages} pages DE/FR/IT : {variants} variantes, {samples} exemples. Même source figée des deux côtés. Aucun changement au canonical ou aux sites publiés.</p>
<label for="case">Variante à examiner</label><select id="case">{options}</select>
<p>Les boutons Avant et Après affichent le même exemple sur toute la largeur. Les liens ouvrent l'ensemble des cas. Les cas conservés ne sont pas nécessairement des erreurs.</p>
<nav class="view-controls" aria-label="État du rendu"><button type="button" data-view="before" aria-pressed="false">Avant</button><button type="button" data-view="after" aria-pressed="true">Après</button></nav><div class="panels"><section data-panel="before" hidden><h2>État actuel</h2><a href="{before}" target="_blank">Tous les exemples avant</a><iframe id="before" title="État actuel"></iframe></section><section data-panel="after"><h2>Proposition corrigée</h2><a href="{after}" target="_blank">Tous les exemples après</a><iframe id="after" title="Proposition corrigée"></iframe></section></div>
<script>const select=document.getElementById('case');function choose(){document.getElementById('before').src=BEFORE+'#'+select.value;document.getElementById('after').src=AFTER+'#'+select.value;}select.addEventListener('change',choose);document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{const view=button.dataset.view;document.querySelectorAll('[data-panel]').forEach(panel=>panel.hidden=panel.dataset.panel!==view);document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));}));choose();</script></html>"""
    # Replace fixed placeholders only, leaving CSS and JavaScript braces intact.
    for key, value in {'pages':report['pages_scanned'], 'variants':len(groups), 'samples':first['samples'],
                       'options':options, 'before':html.escape(b,quote=True), 'after':html.escape(a,quote=True)}.items():
        page = page.replace('{'+key+'}', str(value))
    page = page.replace('BEFORE', json.dumps(b)).replace('AFTER',json.dumps(a))
    output.write_text(page)
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    audit = sub.add_parser('scan')
    audit.add_argument('--site-root',type=Path,required=True)
    audit.add_argument('--output',type=Path,required=True)
    demo = sub.add_parser('preview')
    demo.add_argument('--report',type=Path,required=True)
    demo.add_argument('--output',type=Path,required=True)
    demo.add_argument('--phase',choices=['before','after'],required=True)
    demo.add_argument('--assets-from',type=Path,help='Use a frozen asset directory, especially for historical Before previews.')
    comparison = sub.add_parser('compare')
    comparison.add_argument('--report',type=Path,required=True)
    comparison.add_argument('--before',type=Path,required=True)
    comparison.add_argument('--after',type=Path,required=True)
    comparison.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='scan':
        scan(args.site_root,args.output)
    elif args.command=='preview':
        preview(args.report,args.output,args.phase,assets_from=args.assets_from)
    else:
        compare(args.report,args.before,args.after,args.output)


if __name__=='__main__':
    main()
