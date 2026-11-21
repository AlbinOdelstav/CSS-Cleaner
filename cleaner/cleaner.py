import os
import re
from css_parser import parse, split_selectors, selector_tokens, strip_comments

ANIMATION_RE = re.compile(r"animation(?:-name)?\s*:\s*([^;}]+)", re.I)

# Comments on the lines directly above a rule (no blank line in between)
_COMMENT = r"/\*(?:(?!\*/)[\s\S])*\*/"
LEADING_COMMENTS_RE = re.compile(
    r"(?:^|(?<=\n))(?:[ \t]*" + _COMMENT + r"[ \t]*\n)*[ \t]*" + _COMMENT + r"[ \t]*\n?[ \t]*$")


def _drop_leading_comments(out):
    """Removes the comments that belong to a rule that was just removed."""
    if out:
        out[-1] = LEADING_COMMENTS_RE.sub("", out[-1])


def _filter_rules(nodes, unused, used_animations):
    """Marks which selectors of each rule to keep.

    A selector can never match if it requires a class, id or tag that is not
    used anywhere, so the whole selector is dropped (not just that part of it,
    which would make the selector match more elements than before).
    """
    for node in nodes:
        if node["kind"] == "rule":
            selectors = split_selectors(node["prelude"])
            kept = [s for s in selectors
                    if not any(token in unused for token in selector_tokens(s))]
            node["kept"] = kept
            node["changed"] = len(kept) != len(selectors)
            if kept:
                for value in ANIMATION_RE.findall(strip_comments(node["body"])):
                    used_animations.update(name.strip("\"'") for name in re.split(r"[\s,]+", value) if name)
        elif node["kind"] == "group":
            _filter_rules(node["children"], unused, used_animations)


def _join_selectors(prelude, kept):
    trailing = prelude[len(prelude.rstrip()):]
    separator = ",\n" if "\n" in prelude.strip() else ", "
    return separator.join(s.strip() for s in kept) + trailing


def _render(nodes, used_animations):
    out = []
    for node in nodes:
        kind = node["kind"]
        if kind == "text":
            out.append(node["text"])
        elif kind == "rule":
            if not node["kept"]:
                _drop_leading_comments(out)
                continue
            if node["changed"]:
                out.append(_join_selectors(node["prelude"], node["kept"]) + "{" + node["body"] + node["close"])
            else:
                out.append(node["raw"])
        elif kind == "group":
            inner = _render(node["children"], used_animations)
            if strip_comments(inner).strip():
                out.append(node["prelude"] + "{" + inner + node["close"])
            else:
                _drop_leading_comments(out)
        elif kind == "keyframes":
            # Keyframes are only kept if a remaining rule refers to them
            if node["name"] in used_animations:
                out.append(node["raw"])
            else:
                _drop_leading_comments(out)
        else:
            out.append(node["raw"])
    return "".join(out)


CLEAN_SUFFIX = ".clean.css"


def output_location(css_location):
    """index.css -> index.clean.css, next to the original file."""
    base, _extension = os.path.splitext(css_location)
    return base + CLEAN_SUFFIX


def clean(css_location, css_list):
    """Writes a cleaned copy of css_location and returns its path."""
    unused = {(css["type"], css["value"]) for css in css_list}

    with open(css_location, mode='r', encoding='utf-8') as in_file:
        nodes = parse(in_file.read())

    used_animations = set()
    _filter_rules(nodes, unused, used_animations)
    output = _render(nodes, used_animations)
    # Removed rules leave their surrounding blank lines behind
    output = re.sub(r"\n([ \t]*\n){2,}", "\n\n", output)

    out_location = output_location(css_location)
    with open(out_location, mode='w', encoding='utf-8') as out_file:
        out_file.write(output)
    return out_location
