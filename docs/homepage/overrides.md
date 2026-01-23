Homepage overrides guide

Purpose
- Keep the Framer export intact (layout, animations, responsive behavior).
- Allow safe edits to text, images, and icons without touching Framer JS.

How it works
- `docs/index.html` includes `homepage/overrides.js`.
- `homepage/overrides.js` loads `homepage/overrides.json` and applies:
  - text replacements
  - attribute replacements (e.g., icon URLs)
  - image replacements by URL substring
- A MutationObserver re-applies overrides after Framer re-renders.

Edit overrides.json

Text replacement example
{
  "textReplacements": [
    { "match": "WATCH", "replace": "INVENTORY" }
  ],
  "attributeReplacements": [],
  "imageReplacements": []
}

Scoped text replacement (limits to a selector)
{
  "textReplacements": [
    { "match": "WATCH", "replace": "INVENTORY", "selector": "[data-framer-name='Hero']" }
  ]
}

Replace an icon by selector
{
  "attributeReplacements": [
    {
      "selector": "[data-framer-name='Header Logo'] img",
      "attribute": "src",
      "value": "homepage/assets/site-logo.png"
    }
  ]
}

Replace images by URL substring
{
  "imageReplacements": [
    { "matchSrcIncludes": "framerusercontent.com/images/", "replaceSrc": "homepage/assets/my-hero.jpg" }
  ]
}

Notes
- Use stable selectors if possible (`data-framer-name` or `aria-label`).
- You can add multiple entries to each list.
