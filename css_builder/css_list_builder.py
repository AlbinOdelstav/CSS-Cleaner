from common import extract_id
import re
import os


class Builder:
    def __init__(self, filename):
        self.css_block = False
        self.filename = filename

    def build_css_list(self):
        css_list = []
        with open(self.filename, mode='r', encoding='utf-8') as in_file, \
                open('temp', mode='w+', encoding='utf-8') as temp_file:

            # Removes comments
            reg = re.compile(r"/\*(.+|\s+|[\s\S]+)\*/")
            results = re.sub(reg, "", in_file.read())
            temp_file.write(results)
            in_file.close()

            temp_file.seek(0)
            for line in temp_file:
                for prepared_html_id in line.split():
                    if prepared_html_id.count('.') > 1:
                        html_ids = prepared_html_id.split('.')
                        for i in range(0, len(html_ids)):
                            html_ids[i] = "." + html_ids[i]
                    else:
                        html_ids = [prepared_html_id]
                    for html_id in html_ids:
                        if not self.css_block:
                            if html_id == '{':
                                self.css_block = True
                                continue
                            html_id = extract_id(html_id)
                            if html_id["type"] is not None:
                                if html_id not in css_list:
                                    css_list.append(html_id)
                        else:
                            if html_id == '}':
                                self.css_block = False
            temp_file.close()
            os.remove('temp')
            return css_list
