### About CSS Cleaner
CSS Cleaner removes CSS elements from your CSS files that are no longer used in any of your template files. You were too busy focusing on the template and forgot to clean your CSS file, now it is extremely cluttered and it drives you crazy, so here we are.

### Usage
Run cssc.py and follow the instructions.

### Under development
CSS Cleaner is still under development and should not yet be used for big projects, as it will probably break your code. See [Issues](https://github.com/AlbinOdelstav/CSS-Cleaner/issues) for some of the known issues.
#### Some things that will break your code
- [#5](https://github.com/AlbinOdelstav/CSS-Cleaner/issues/5) Comments /* */
- [#7](https://github.com/AlbinOdelstav/CSS-Cleaner/issues/7) @ (at-rules)
- [#10](https://github.com/AlbinOdelstav/CSS-Cleaner/issues/10) \* (CSS universal selectors)
- CSS elements used only in script files like JavaScript or TypeScript, these elements has to be excluded from the options.
- Probably more things that has to be investigated
