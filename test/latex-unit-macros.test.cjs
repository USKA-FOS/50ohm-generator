const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const katex = require('../assets/katex/katex.min.js');

const source = fs.readFileSync(path.join(__dirname, '../assets/latex.js'), 'utf8');
let macros;
vm.runInNewContext(source, {
  document: {
    body: {},
    addEventListener(_event, callback) { callback(); },
  },
  renderMathInElement(_body, options) { macros = options.macros; },
});

test('site renders canonical gram, minute and dBm units', () => {
  for (const expression of [
    String.raw`\qty{210}{\gram}`,
    String.raw`\qty{30}{\minute}`,
    String.raw`\qty{-5}{\text{dBm}}`,
    String.raw`\qty{15}{\farad}`,
    String.raw`\qty{10}{\mega\text{sample}\per\second}`,
  ]) {
    assert.doesNotThrow(() => katex.renderToString(expression, {
      throwOnError: true,
      strict: 'ignore',
      macros,
    }), expression);
  }
});
