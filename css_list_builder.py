def extract_id(html_id):
    html_id = html_id.replace(',', '')
    id_obj = {"type": None, "value": None}

    if html_id == '<' or html_id == '>' or html_id == '':
        return id_obj

    if ':' in html_id:
        html_id = html_id.split(':')[0]
    if html_id[0] == '#':
        id_obj = {"type": "id", "value": html_id.replace('#', ''), "used": False}
    elif html_id[0] == '.':
        id_obj = {"type": "class", "value": html_id.replace('.', ''), "used": False}
    else:
        id_obj = {"type": "tag", "value": html_id, "used": False}
    return id_obj


def build_css_list(filename):
    css_list = []
    file = open(filename, mode='r', encoding='utf-8')
    css_block = False

    for line in file:
        for prepared_html_id in line.split():
            if prepared_html_id.count('.') > 1:
                html_ids = prepared_html_id.split('.')
                for i in range(0, len(html_ids)):
                    html_ids[i] = "." + html_ids[i]
            else:
                html_ids = [prepared_html_id]
            for html_id in html_ids:
                if not css_block:
                    if html_id == '{':
                        css_block = True
                        continue
                    html_id = extract_id(html_id)
                    if html_id["type"] is not None:
                        if html_id not in css_list:
                            css_list.append(html_id)
                else:
                    if html_id == '}':
                        css_block = False
    return css_list
