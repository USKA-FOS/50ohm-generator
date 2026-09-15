const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../assets/language-switch.js"), "utf8");

function run(href, saved = null, storageDisabled = false) {
  const links = ["de", "fr", "it"].map((language) => ({
    dataset: { siteLanguage: language },
    addEventListener(type, callback) { this.click = callback; },
  }));
  const state = { saved, links };
  const window = {
    location: { href }, scrollX: 12, scrollY: 980,
    addEventListener(type, callback) { state.load = callback; },
    requestAnimationFrame(callback) { callback(); },
    scrollTo(x, y) { state.scrolled = [x, y]; },
  };
  vm.runInNewContext(source, {
    URL, window,
    document: { querySelectorAll: () => links, fonts: { ready: Promise.resolve() } },
    sessionStorage: {
      getItem() { if (storageDisabled) throw Error("disabled"); return state.saved; },
      setItem(key, value) { if (storageDisabled) throw Error("disabled"); state.saved = value; },
      removeItem() { state.saved = null; },
    },
  });
  return state;
}

test("keeps the deployment prefix, page, query and anchor", () => {
  const state = run("https://example.test/beta/de/NE_transistor.html?q=1#question");
  assert.equal(state.links[1].href, "https://example.test/beta/fr/NE_transistor.html?q=1#question");
  assert.equal(state.links[2].href, "https://example.test/beta/it/NE_transistor.html?q=1#question");
});

test("saves and restores scroll on the target page", async () => {
  const state = run("https://example.test/de/index.html");
  state.links[1].click({ button: 0 });
  const target = run(state.links[1].href, state.saved);
  await target.load();
  assert.deepEqual(target.scrolled, [12, 980]);
  assert.equal(target.saved, null);
});

test("does not restore another page or intercept modified clicks", async () => {
  const state = run("https://example.test/de/index.html");
  state.links[1].click({ button: 0, ctrlKey: true });
  assert.equal(state.saved, null);
  const target = run("https://example.test/it/index.html", JSON.stringify({ url: state.links[1].href, x: 0, y: 900 }));
  await target.load();
  assert.equal(target.scrolled, undefined);
});

test("language links still work with disabled storage", async () => {
  const state = run("https://example.test/fr/index.html", null, true);
  assert.equal(state.links[2].href, "https://example.test/it/index.html");
  state.links[2].click({ button: 0 });
  await state.load();
  assert.equal(state.scrolled, undefined);
});
