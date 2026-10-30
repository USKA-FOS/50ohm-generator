const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');
const katex = require('../assets/katex/katex.min.js');
const inline = require('../assets/formula-inline.js');
let options = [];
vm.runInNewContext(fs.readFileSync(require.resolve('../assets/latex.js'), 'utf8'), {
 document: {body:{}, documentElement:{dataset:{formulaPresentation:'contextual'}},
   addEventListener(_, fn) {fn();}},
 OhmInlineMath: inline,
 renderMathInElement(_, opt) {options.push(opt);}
});
const macros = options[1].macros;

test('display math stays native and only inline math is preprocessed', () => {
 assert.equal(options.length, 2);
 assert.equal(options[0].preProcess, undefined);
 assert.equal(typeof options[1].preProcess, 'function');
 assert.equal(options[0].delimiters.every(d => d.display), true);
 assert.equal(options[1].delimiters.every(d => !d.display), true);
});
test('native sans fonts preserve italic variable and upright units', () => {
 const tex = inline.convert(String.raw`U_i = \qty{230}{\volt}`);
 const html = katex.renderToString(tex, {macros, throwOnError:true});
 assert.match(html, /textsf textit/);
 assert.match(html, /mathsf|textsf/);
 assert.match(tex, /\\mathsfit\{i\}/);
 assert.match(tex, /\\qty\{230\}\{\\volt\}/);
});
test('accents, fractions, functions, metadata and explicit fonts stay renderable', () => {
 for (const source of [String.raw`\hat U = \frac{R_L}{\sqrt{2}}`,
 String.raw`\sin(\omega t)`, String.raw`\text{eff} + \mathrm{L}`,
 String.raw`\begin{aligned}U&=RI\end{aligned}`, String.raw`\mathbb{R}`]) {
  assert.doesNotThrow(() => katex.renderToString(inline.convert(source), {macros, throwOnError:true}), source);
 }
 assert.match(inline.convert(String.raw`\mathbb{R}`), /\\mathbb\{R\}/);
 assert.match(inline.convert(String.raw`\begin{aligned}`), /\\begin\{aligned\}/);
});
