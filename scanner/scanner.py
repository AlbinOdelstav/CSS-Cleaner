import re


def get_result_keyword_arr(match):
    match = match.replace("class=\"", "")
    match = match.replace("id=\"", "")
    match = match.replace("<", "")
    match = match.replace(">", "")
    match = match.replace("\"", "")
    match = match.replace("\'", "")
    return match.split()


def scan_html_files(filenames, css_list):
    for i in range(len(css_list)):
        for filename in filenames:
            file = open(filename, mode='r', encoding='utf-8').read()
            if css_list[i]["type"] == "class":
                reg = re.compile("class=[\"|\'].+[\"|\']")
            elif css_list[i]["type"] == "id":
                reg = re.compile("id=[\"|\'].+[\"|\']")
            else:
                reg = re.compile("<" + re.escape(css_list[i]["value"]))
            results = re.findall(reg, file)
            if results is None:
                continue
            for result in results:
                result_arr = get_result_keyword_arr(result)
                for keyword in result_arr:
                    if css_list[i]["value"] == keyword:
                        css_list[i]["used"] = True
                        continue
                if css_list[i]["used"]:
                    continue
            if css_list[i]["used"]:
                continue
    return list(filter(lambda x: x["used"] is False, css_list))
