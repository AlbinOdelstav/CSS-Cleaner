def is_unused_element(html_id, css_list):
    for css in css_list:
        if html_id["value"] == css["value"] and html_id["type"] == css["type"]:
            return True
    return False


def get_value(css):
    value = css["value"]
    if css["type"] == "class":
        value = "." + value
    elif css["type"] == "id":
        value = "#" + value
    return value


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