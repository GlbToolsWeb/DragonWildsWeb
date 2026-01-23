(() => {
  const overridesUrl = "homepage/overrides.json";
  let cachedOverrides = null;
  let applying = false;

  const applyTextReplacements = (replacements) => {
    if (!Array.isArray(replacements)) return;
    replacements.forEach(({ match, replace, selector }) => {
      if (!match) return;
      const roots = selector ? document.querySelectorAll(selector) : [document.body];
      roots.forEach((root) => {
        const walker = document.createTreeWalker(
          root,
          NodeFilter.SHOW_TEXT,
          {
            acceptNode: (node) => {
              const text = node.nodeValue;
              if (!text || !text.includes(match)) return NodeFilter.FILTER_REJECT;
              if (node.parentElement?.closest("script, style")) {
                return NodeFilter.FILTER_REJECT;
              }
              return NodeFilter.FILTER_ACCEPT;
            },
          }
        );
        const nodes = [];
        let current = walker.nextNode();
        while (current) {
          nodes.push(current);
          current = walker.nextNode();
        }
        nodes.forEach((node) => {
          node.nodeValue = node.nodeValue.split(match).join(replace);
        });
      });
    });
  };

  const applyAttributeReplacements = (replacements) => {
    if (!Array.isArray(replacements)) return;
    replacements.forEach(({ selector, attribute, value }) => {
      if (!selector || !attribute) return;
      document.querySelectorAll(selector).forEach((el) => {
        el.setAttribute(attribute, value);
      });
    });
  };

  const applyImageReplacements = (replacements) => {
    if (!Array.isArray(replacements)) return;
    replacements.forEach(({ matchSrcIncludes, replaceSrc }) => {
      if (!matchSrcIncludes || !replaceSrc) return;
      document.querySelectorAll("img").forEach((img) => {
        const srcMatches = img.src && img.src.includes(matchSrcIncludes);
        const srcsetMatches = img.srcset && img.srcset.includes(matchSrcIncludes);
        const markedMatch = img.dataset.overrideImageMatch === matchSrcIncludes;
        if (srcMatches || srcsetMatches || markedMatch) {
          img.dataset.overrideImageMatch = matchSrcIncludes;
          if (img.src !== replaceSrc) {
            img.src = replaceSrc;
          }
          if (img.hasAttribute("srcset")) {
            img.removeAttribute("srcset");
          }
        }
      });
    });
  };

  const applyOverrides = (overrides) => {
    if (applying) return;
    applying = true;
    applyTextReplacements(overrides.textReplacements);
    applyAttributeReplacements(overrides.attributeReplacements);
    applyImageReplacements(overrides.imageReplacements);
    requestAnimationFrame(() => {
      applying = false;
    });
  };

  const observeChanges = () => {
    const observer = new MutationObserver(() => {
      if (cachedOverrides) applyOverrides(cachedOverrides);
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: false,
    });
  };

  const start = async () => {
    try {
      const response = await fetch(overridesUrl, { cache: "no-store" });
      if (!response.ok) return;
      cachedOverrides = await response.json();
      applyOverrides(cachedOverrides);
      observeChanges();
    } catch (error) {
      console.warn("Overrides failed to load", error);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
