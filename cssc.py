import os
import sys
import re


def print_help():
    print("help")


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


def evaluate_html_id(html_id):
    print("\nYou chose: " + html_id)
    print("1. Change")
    if " [EXCLUDED]" not in html_id:
        print("2. Exclude")
    else:
        print("2. Include")
    print("0. Go back")
    user_input = input(": ")
    while not user_input.isdigit() or not 0 < int(user_input) < 2:
        user_input = input("Provide a number from the options: ")

    if int(user_input) == 1:
        html_id = input("New name: ")
        return html_id
    if int(user_input) == 2:
        return -1


def evaluate_list(css_list):
    limit = 10
    offset = 0
    length = (len(css_list) // limit) + 1
    excluded_list = []
    while offset < length:
        print("----------------------------------------------------------------------------")
        print("Page", str((offset + 1)) + "/" + str(length))
        print("----------------------------------------------------------------------------")
        for index in range(limit):
            if index + (limit * offset) >= len(css_list):
                break

            html_id = css_list[index + (limit * offset)]["value"]
            print(str(index + 1) + ": " + html_id)

        print("----------------------------------------------------------------------------")
        user_input = input("Input a number for options, press enter to proceed or type exit to stop: ")
        if user_input.isdigit():
            chosen_index = (int(user_input) - 1) + (limit * offset)
            modified_html_id = evaluate_html_id(css_list[chosen_index]["value"])
            if modified_html_id == -1:
                if " [EXCLUDED]" not in css_list[chosen_index]:
                    css_list[chosen_index]["value"] = css_list[chosen_index]["value"] + " [EXCLUDED]"
                    excluded_list.append(chosen_index)
                else:
                    css_list[chosen_index]["value"] = css_list[chosen_index]["value"].split(" [EXCLUDED]")[0]
                    excluded_list.remove(chosen_index)
            else:
                css_list[chosen_index]["value"] = modified_html_id
            offset = offset - 1
        elif user_input == "exit":
            return css_list
        offset = offset + 1

    removed_items = 0
    for index in excluded_list:
        css_list.pop(index - removed_items)
        removed_items = removed_items + 1
    return css_list


def is_unused_element(html_id, css_list):
    for css in css_list:
        if html_id["value"] == css["value"] and html_id["type"] == css["type"]:
            return True
    return False


def delete_all(css_location, css_list):
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


def scan_html_files(filenames, css_list):
    for i in range(len(css_list)):
        for filename in filenames:
            file = open(filename, mode='r', encoding='utf-8').read()
            if css_list[i]["type"] == "class":
                reg = re.compile("class=." + re.escape(css_list[i]["value"]) + ".")
            elif css_list[i]["type"] == "id":
                reg = re.compile("id=." + re.escape(css_list[i]["value"]) + ".")
            else:
                reg = re.compile("<" + re.escape(css_list[i]["value"]))

            if bool(re.search(reg, file)):
                css_list[i]["used"] = True
                continue

    css_list = list(filter(lambda x: x["used"] is False, css_list))

    return css_list


def get_html_locations():
    html_locations = []

    while True:
        html_location = input("HTML directory location: ")
        if not os.path.exists(html_location):
            print("Directory not found")
        else:
            if html_location[-1:] != "\\":
                html_location = html_location + "\\"
            if html_location not in html_locations:
                html_locations.append(html_location)
                print("\nDirectories that will be scanned:")
                for directory in html_locations:
                    print(directory)
            else:
                print("Directory already added")
            print("\nOptions:")
            print("1. Add one more")
            print("2. Done")
            user_input = input(": ")
            while user_input != "1" and user_input != "2":
                user_input = input("Provide a number from the options: ")
            if int(user_input) == 2:
                break
    extensions = input("HTML extensions, separate with space (e.g html ejs): ").split()

    final_directories = []
    try:
        for directory in html_locations:
            for extension in extensions:
                filenames = [directory + filename for filename in os.listdir(directory)]
                filenames = list(filter(lambda x: (x[-len(extension):] == extension), filenames))
                final_directories.extend(filenames)
    except:
        print("Woops, something went wrong")
        sys.exit()

    if not final_directories:
        print("No files with the provided extensions found")
        sys.exit()

    print("Found html files:")
    for filename in final_directories:
        print(filename)

    return final_directories


def main():
    css_location = input("CSS file location (e.g C:\\Users\\username\\TestProject\\src\\css\\index.css):\n")

    if not os.path.isfile(css_location):
        print("File not found")
        sys.exit()

    html_files = get_html_locations()

    print("\nBuilding CSS list..")
    css_list = build_css_list(css_location)

    print("Done!\nThis program does not take CSS that is used in script files such as "
          "JavaScript or TypeScript into account, you need to exclude these from the options. "
          "Would you like to go through the list and do that and/or correct eventual errors? [y/n]: ", end='')
    if input() == 'y':
        print("")
        css_list = evaluate_list(css_list)

    print("\nScanning files..")
    css_list = scan_html_files(html_files, css_list)

    if css_list:
        print("Found " + str(len(css_list)) + " unused CSS elements:")
        for i in range(0, len(css_list)):
            value = get_value(css_list[i])
            print(str((i + 1)) + ". " + value)

        print("\nOptions:")
        print("1. Trust this sketchy program and delete all")
        print("2. Select which ones to delete")
        print("0. Exit and go on with your life, maybe have a coffee or something")
        user_input = input()

        while user_input != "1" and user_input != "2" and user_input != "0":
            user_input = input("Provide a number from the options: ")

        if int(user_input) == 1:
            delete_all(css_location, css_list)
        if int(user_input) == 2:
            print("Bummer, this option has not been implemented yet :(")


if __name__ == "__main__":
    main()