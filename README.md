### About CSS Cleaner
CSS Cleaner removes CSS rules from your CSS files that are no longer used in any of your template files. You were too busy focusing on the template and forgot to clean your CSS file, now it is extremely cluttered and it drives you crazy, so here we are.

### Requirements
Python 3.6 or later. No other dependencies.

### Usage
Run `python cssc.py` and follow the instructions:

1. **CSS files** – add one or more CSS files, or a directory to clean every `.css` file in it (subdirectories included).
2. **Template directories** – add the directories with your templates. Subdirectories are scanned too, `node_modules` and `.git` are skipped.
3. **Extensions** – the template file extensions to scan, e.g. `html ejs`.
4. **Review the list (optional)** – exclude classes, ids or tags that must be kept, e.g. ones only used from JavaScript.
5. **Delete** – delete all unused elements, or pick which ones.

The original files are never changed. A cleaned copy is written next to each file, e.g. `index.css` → `index.clean.css`. Compare the two before replacing the original.

### How it works
- Every class, id and tag used in a selector is collected from the CSS files and searched for in the templates.
- A selector that requires an element that is not used anywhere can never match, so the whole selector is removed. If all selectors of a rule are removed, the rule is removed, together with the comment directly above it.
  - `.used .unused { }` is removed completely, it does not become `.used { }`.
  - `.used, .unused { }` becomes `.used { }`.
- Rules inside `@media`, `@supports`, `@layer` and `@container` are cleaned the same way. A block that ends up empty is removed.
- `@keyframes` are kept only if a remaining rule uses them in `animation` or `animation-name`.
- Other at-rules (`@import`, `@font-face`, `@charset`, ...) are kept as they are.
- Arguments of pseudo-classes such as `:not(.x)`, attribute selectors and the universal selector `*` never count as required.

### Limitations
CSS Cleaner is still under development, always review the output before using it.
- **JavaScript/TypeScript:** classes, ids and keyframes that are only used from scripts (or added dynamically) are not detected. Exclude them in step 4.
- **Templates:** only `class="..."` and `id="..."` attributes and `<tag` are searched for. Framework bindings like `:class` or `className` and classes built from template expressions are not detected.
- A selector is kept as long as each of its parts is used *somewhere*, even if they never appear together on the same element. The output can therefore contain rules that are not needed, but it should not remove rules that are.

See [Issues](https://github.com/AlbinOdelstav/CSS-Cleaner/issues) for known problems.
