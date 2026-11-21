from css_parser import parse, split_selectors, selector_tokens


class Builder:
    def __init__(self, filename):
        self.filename = filename

    def build_css_list(self):
        """Collects every class, id and tag used in a selector in the CSS file."""
        with open(self.filename, mode='r', encoding='utf-8') as in_file:
            nodes = parse(in_file.read())

        css_list = []
        seen = set()

        def walk(nodes):
            for node in nodes:
                if node["kind"] == "rule":
                    for selector in split_selectors(node["prelude"]):
                        for kind, value in selector_tokens(selector):
                            if (kind, value) not in seen:
                                seen.add((kind, value))
                                css_list.append({"type": kind, "value": value, "used": False})
                elif node["kind"] == "group":
                    walk(node["children"])

        walk(nodes)
        return css_list
