"""Minimal CSS parser.

Splits a stylesheet into rules and at-rules while keeping the original text,
so the cleaner can rewrite only the parts it removes. Comments and strings are
skipped when looking for braces, and nested blocks (@media, @keyframes, ...)
are matched by depth instead of by line.
"""
import re

# At-rules whose block contains ordinary style rules
GROUP_AT_RULES = ("media", "supports", "layer", "container", "document", "scope", "starting-style")

KEYFRAMES_RE = re.compile(r"@(?:-[a-z]+-)?keyframes\s+([^\s{]+)", re.I)
AT_NAME_RE = re.compile(r"@([\w-]+)")
COMMENT_RE = re.compile(r"/\*[\s\S]*?\*/")

_IDENT = r"(?:[\w-]|\\.)+"
_CLASS_RE = re.compile(r"(?<!\\)\.(" + _IDENT + ")")
_ID_RE = re.compile(r"(?<!\\)#(" + _IDENT + ")")
_TAG_RE = re.compile(r"(?:^|(?<=[\s>+~]))([a-zA-Z][\w-]*)")
_ATTRIBUTE_RE = re.compile(r"\[(?:[^\]\"']|\"[^\"]*\"|'[^']*')*\]")
_PSEUDO_WITH_ARGS_RE = re.compile(r"(?<!\\)::?[\w-]+\([^()]*\)")
_PSEUDO_RE = re.compile(r"(?<!\\)::?[\w-]+")


def strip_comments(text):
    return COMMENT_RE.sub("", text)


def _skip_comment_or_string(text, i):
    """If a comment or string starts at i, return the index just after it, else None."""
    if text.startswith("/*", i):
        end = text.find("*/", i + 2)
        return len(text) if end == -1 else end + 2
    if text[i] in "\"'":
        quote = text[i]
        j = i + 1
        while j < len(text):
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == quote or text[j] == "\n":
                return j + 1
            j += 1
        return len(text)
    return None


def _find_block_end(text, start):
    """start is the index just after '{'. Returns the index of the matching '}'."""
    depth = 1
    i = start
    while i < len(text):
        skip = _skip_comment_or_string(text, i)
        if skip is not None:
            i = skip
            continue
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text)


def parse(text):
    """Returns a list of nodes. Each node has a "kind":

    text      - whitespace, comments or statements kept verbatim ("text")
    rule      - style rule ("prelude", "body")
    group     - @media/@supports/... ("prelude", "children")
    keyframes - @keyframes ("name", "raw")
    at        - any other block at-rule, kept verbatim ("raw")
    """
    nodes = []
    i, n = 0, len(text)
    while i < n:
        # Whitespace and comments between rules are kept as they are
        start = i
        while i < n:
            if text[i].isspace():
                i += 1
            elif text.startswith("/*", i):
                i = _skip_comment_or_string(text, i)
            else:
                break
        if i > start:
            nodes.append({"kind": "text", "text": text[start:i]})
        if i >= n:
            break

        # Prelude: everything up to '{' (or ';' for statements like @import)
        start = i
        while i < n and text[i] not in "{;}":
            skip = _skip_comment_or_string(text, i)
            if skip is not None:
                i = skip
            elif text[i] == "\\":
                i += 2
            else:
                i += 1
        prelude = text[start:i]

        if i >= n or text[i] != "{":
            end = min(i + 1, n)
            nodes.append({"kind": "text", "text": text[start:end]})
            i = end
            continue

        body_end = _find_block_end(text, i + 1)
        node = {
            "prelude": prelude,
            "body": text[i + 1:body_end],
            "close": "}" if body_end < n else "",
            "raw": text[start:body_end + 1],
        }
        i = body_end + 1

        keyframes = KEYFRAMES_RE.match(prelude)
        at_name = AT_NAME_RE.match(prelude)
        if keyframes:
            node["kind"] = "keyframes"
            node["name"] = keyframes.group(1).strip("\"'")
        elif at_name and at_name.group(1).lower() in GROUP_AT_RULES:
            node["kind"] = "group"
            node["children"] = parse(node["body"])
        elif at_name:
            node["kind"] = "at"
        else:
            node["kind"] = "rule"
        nodes.append(node)
    return nodes


def split_selectors(prelude):
    """Splits a selector list on top-level commas (not inside () or [])."""
    parts = []
    depth = 0
    part_start = 0
    i = 0
    while i < len(prelude):
        skip = _skip_comment_or_string(prelude, i)
        if skip is not None:
            i = skip
            continue
        c = prelude[i]
        if c == "\\":
            i += 2
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(prelude[part_start:i])
            part_start = i + 1
        i += 1
    parts.append(prelude[part_start:])
    return parts


def _unescape(name):
    return re.sub(r"\\(.)", r"\1", name)


def selector_tokens(selector):
    """Returns the (type, value) pairs a single selector requires to exist.

    Arguments of pseudo-classes like :not(.x) are ignored, since they do not
    require .x to exist. The universal selector * yields nothing.
    """
    s = strip_comments(selector)
    s = _ATTRIBUTE_RE.sub("", s)
    previous = None
    while previous != s:
        previous = s
        s = _PSEUDO_WITH_ARGS_RE.sub("", s)
    s = _PSEUDO_RE.sub("", s)

    tokens = []
    for pattern, kind in ((_CLASS_RE, "class"), (_ID_RE, "id")):
        tokens += [(kind, _unescape(value)) for value in pattern.findall(s)]
        s = pattern.sub(" ", s)
    tokens += [("tag", tag.lower()) for tag in _TAG_RE.findall(s)]

    unique = []
    for token in tokens:
        if token not in unique:
            unique.append(token)
    return unique
