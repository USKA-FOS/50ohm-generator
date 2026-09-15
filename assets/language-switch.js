(() => {
  const storageKey = "50ohm-language-scroll";
  const links = document.querySelectorAll("[data-site-language]");
  for (const link of links) {
    const url = new URL(window.location.href);
    const language = link.dataset.siteLanguage;
    if (/\/(de|fr|it)\//.test(url.pathname)) {
      url.pathname = url.pathname.replace(/\/(de|fr|it)\//, `/${language}/`);
    } else {
      const filename = url.pathname.split("/").pop() || "index.html";
      url.pathname = new URL(`../${language}/${filename}`, url).pathname;
    }
    link.href = url.href;
    link.addEventListener("click", (event) => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      try {
        sessionStorage.setItem(storageKey, JSON.stringify({
          url: link.href, x: window.scrollX, y: window.scrollY,
        }));
      } catch {
        // Navigation remains available when browser storage is disabled.
      }
    });
  }

  window.addEventListener("load", async () => {
    let position;
    try {
      position = JSON.parse(sessionStorage.getItem(storageKey));
      if (!position || position.url !== window.location.href) return;
      sessionStorage.removeItem(storageKey);
    } catch {
      return;
    }
    if (document.fonts) await document.fonts.ready;
    window.requestAnimationFrame(() => window.scrollTo(position.x, position.y));
  }, { once: true });
})();
