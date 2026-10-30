/* Native KaTeX font selection for inline math only. No canonical rewriting.
 * Keep specialised/unknown commands and their arguments intact. Greek and
 * unsupported glyphs retain KaTeX's built-in font fallback and metrics.
 */
(function (root) {
  function groupEnd(source, start) {
    let depth = 0;
    for (let i = start; i < source.length; i++) {
      if (source[i] === "\\") { i++; continue; }
      if (source[i] === "{") depth++;
      if (source[i] === "}" && --depth === 0) return i + 1;
    }
    return -1;
  }
  const fonts = new Set(["text", "textrm", "mathrm", "textsf", "symup", "operatorname",
    "mathsf", "mathsfit", "mathit", "mathnormal", "mathbf", "boldsymbol", "bm",
    "mathbb", "mathcal", "mathscr", "mathfrak", "mathtt", "textbf", "textit"]);
  const mathCommands = new Set(["frac", "dfrac", "tfrac", "sqrt", "hat", "widehat",
    "bar", "overline", "underline", "vec", "dot", "ddot", "overset", "underset",
    "underbrace", "overbrace", "left", "right", "big", "Big", "bigg", "Bigg"]);
  const functions = new Set(["sin", "cos", "tan", "cot", "sinh", "cosh", "tanh",
    "arcsin", "arccos", "arctan", "log", "ln", "exp"]);
  function convert(source) {
    let out = "";
    for (let i = 0; i < source.length;) {
      if (source[i] === "\\") {
        const match = /^\\([a-zA-Z]+|.)/.exec(source.slice(i));
        if (!match) return source;
        const command = match[1];
        out += match[0]; i += match[0].length;
        if (functions.has(command)) {
          out = out.slice(0, -match[0].length) + "\\operatorname{\\mathsf{" + command + "}}";
          continue;
        }
        if (fonts.has(command)) {
          const single = /^(\s*)([A-Za-z])/.exec(source.slice(i));
          if (single) { out += single[0]; i += single[0].length; continue; }
        }
        if (fonts.has(command) || !mathCommands.has(command)) {
          // These arguments may be text, unit names, colours, environment names
          // or explicit font instructions, not implicit mathematical variables.
          for (;;) {
            let start = i;
            while (/\s/.test(source[start] || "") && start < source.length) start++;
            if (source[start] !== "{") break;
            const end = groupEnd(source, start);
            if (end < 0) return source;
            out += source.slice(i, end); i = end;
          }
        }
      } else if (/[A-Za-z]/.test(source[i])) {
        const letters = /^[A-Za-z]+/.exec(source.slice(i))[0];
        // Do not group an unbraced subscript into the next atom: x_i y is x_i y.
        out += [...letters].map(letter => "{\\mathsfit{" + letter + "}}").join("");
        i += letters.length;
      } else {
        out += source[i++];
      }
    }
    return "\\mathsf{" + out + "}";
  }
  function inlineMacros(macros) {
    return Object.assign({}, macros, {
      "\\mathrm": "\\mathsf{#1}", "\\textrm": "\\textsf{#1}",
      "\\text": "\\textsf{#1}", "\\symup": "\\textsf{#1}",
      "\\mathit": "\\mathsfit{#1}",
      // Bundled KaTeX 0.13.11 lacks the newer native \\mathsfit command.
      // Stacked text-family/shape commands use its real sans-italic metrics.
      "\\mathsfit": "\\textsf{\\textit{#1}}"
    });
  }
  const api = {convert, inlineMacros};
  root.OhmInlineMath = api;
  if (typeof module !== "undefined") module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
