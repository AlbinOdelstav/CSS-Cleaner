from common import extract_id, is_unused_element, get_value
import re


def clean(css_location, css_list):
    with open(css_location, mode='r', encoding='utf-8') as in_file, \
            open('output.css', mode='w', encoding='utf-8') as out_file:

        unused_block = True
        css_block = False
        stored_lines = []

        for line in in_file:
            if not css_block:
                unused_block = True
                for prepared_html_id in line.split():
                    if prepared_html_id.count('.') > 1:
                        html_ids = prepared_html_id.split('.')
                        for i in range(0, len(html_ids)):
                            html_ids[i] = "." + html_ids[i]
                    else:
                        html_ids = [prepared_html_id]

                    for html_id in html_ids:
                        if not html_id == "{":
                            html_id = extract_id(html_id)
                            if html_id["type"] is None:
                                continue

                            if unused_block:
                                unused_block = is_unused_element(html_id, css_list)
                        else:
                            css_block = True
                            if not unused_block:
                                for stored_line in stored_lines:
                                    out_file.write(stored_line)
                                stored_lines = []
                                out_file.write(line)
                            continue

                        if is_unused_element(html_id, css_list):
                            for split in line.split():
                                if get_value(html_id) in split:
                                    line = line.replace(split, "")

                            line = line.replace("  ", "")
                            line = re.sub(r"(.){", r"\1 {", line)
                            line = re.sub(r", {", r" {", line)

                if not css_block and not unused_block:
                    stored_lines.append(line)

            else:
                if line.strip() == "}":
                    if not unused_block:
                        out_file.write(line + "\n")
                    css_block = False
                elif not unused_block:
                    out_file.write(line)
