import os
import sys
from css_builder.css_list_builder import Builder
from scanner.scanner import scan_html_files
from common import get_value
from cleaner.cleaner import clean, CLEAN_SUFFIX


EXCLUDED_LABEL = " [EXCLUDED]"


def menu_evaluate_html_id(css, excluded):
    """Returns ("change", new_name), ("toggle", None) or ("back", None)."""
    print("\nYou chose: " + get_value(css) + (EXCLUDED_LABEL if excluded else ""))
    print("1. Change")
    print("2. Include" if excluded else "2. Exclude")
    print("0. Go back")
    user_input = input(": ").strip()
    while user_input not in ("0", "1", "2"):
        user_input = input("Provide a number from the options: ").strip()

    if user_input == "1":
        new_name = input("New name: ").strip()
        while not new_name:
            new_name = input("Name can not be empty: ").strip()
        return "change", new_name
    if user_input == "2":
        return "toggle", None
    return "back", None


def menu_evaluate_list(css_list):
    limit = 10
    offset = 0
    pages = (len(css_list) + limit - 1) // limit
    excluded = set()  # indexes in css_list

    while offset < pages:
        first = limit * offset
        items_on_page = min(limit, len(css_list) - first)
        print("----------------------------------------------------------------------------")
        print("Page", str(offset + 1) + "/" + str(pages))
        print("----------------------------------------------------------------------------")
        for index in range(items_on_page):
            css_index = first + index
            label = EXCLUDED_LABEL if css_index in excluded else ""
            print(str(index + 1) + ": " + get_value(css_list[css_index]) + label)

        print("----------------------------------------------------------------------------")
        user_input = input("Input a number for options, press enter to proceed or type exit to stop: ").strip()
        if user_input.isdigit():
            if not 1 <= int(user_input) <= items_on_page:
                print("Provide a number between 1 and " + str(items_on_page))
                continue
            chosen_index = first + int(user_input) - 1
            action, new_name = menu_evaluate_html_id(css_list[chosen_index], chosen_index in excluded)
            if action == "toggle":
                excluded ^= {chosen_index}
            elif action == "change":
                css_list[chosen_index]["value"] = new_name
            continue  # show the same page again
        if user_input.lower() == "exit":
            break
        offset = offset + 1

    return [css for index, css in enumerate(css_list) if index not in excluded]


def menu_get_html_locations():
    html_locations = []

    while True:
        html_location = input("HTML directory location: ")
        if not os.path.isdir(html_location):
            print("Directory not found")
        else:
            html_location = os.path.abspath(html_location)
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

    suffixes = tuple("." + extension.lstrip(".").lower() for extension in extensions)
    final_directories = []
    for directory in html_locations:
        # Scans subdirectories too (e.g. partials), but not dependencies
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
            for filename in files:
                path = os.path.join(root, filename)
                if filename.lower().endswith(suffixes) and path not in final_directories:
                    final_directories.append(path)

    if not final_directories:
        print("No files with the provided extensions found")
        sys.exit()

    print("Found html files:")
    for filename in final_directories:
        print(filename)
    return final_directories


def find_css_files(location):
    """A .css file, or every .css file in a directory and its subdirectories."""
    if os.path.isfile(location):
        return [os.path.abspath(location)]
    css_files = []
    for root, dirs, files in os.walk(location):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
        for filename in files:
            if filename.lower().endswith(".css") and not filename.lower().endswith(CLEAN_SUFFIX):
                css_files.append(os.path.abspath(os.path.join(root, filename)))
    return css_files


def menu_get_css_locations():
    css_files = []

    while True:
        css_location = input("CSS file or directory (e.g C:\\Users\\username\\TestProject\\src\\css\\index.css):\n")
        if not os.path.exists(css_location):
            print("File or directory not found")
            continue
        found = [f for f in find_css_files(css_location) if f not in css_files]
        if not found:
            print("No new CSS files found there")
        css_files.extend(found)
        if css_files:
            print("\nCSS files that will be cleaned:")
            for filename in css_files:
                print(filename)
        print("\nOptions:")
        print("1. Add one more")
        print("2. Done")
        user_input = input(": ").strip()
        while user_input not in ("1", "2"):
            user_input = input("Provide a number from the options: ").strip()
        if user_input == "2":
            if css_files:
                return css_files
            print("Add at least one CSS file")


def menu_select_to_delete(css_list):
    """Lets the user pick which of the unused elements to delete."""
    user_input = input("Numbers to delete, separate with space (e.g 1 3 4): ").split()
    while not user_input or not all(n.isdigit() and 1 <= int(n) <= len(css_list) for n in user_input):
        user_input = input("Provide numbers between 1 and " + str(len(css_list)) + ": ").split()
    chosen = {int(n) - 1 for n in user_input}
    return [css for index, css in enumerate(css_list) if index in chosen]


def main():
    css_files = menu_get_css_locations()
    html_files = menu_get_html_locations()

    print("\nBuilding CSS list..")
    css_list = []
    for css_location in css_files:
        for css in Builder(css_location).build_css_list():
            if not any(css["type"] == c["type"] and css["value"] == c["value"] for c in css_list):
                css_list.append(css)

    print("Done!\nThis program does not take CSS that is used in script files such as\n"
          "JavaScript or TypeScript into account, you need to exclude these from the options.\n"
          "Would you like to go through the list and do that and/or correct eventual errors? [y/n]: ", end='')
    if input().strip().lower() in ('y', 'yes'):
        print("")
        css_list = menu_evaluate_list(css_list)

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
        user_input = input().strip()

        while user_input not in ("0", "1", "2"):
            user_input = input("Provide a number from the options: ").strip()

        if user_input == "0":
            return
        if user_input == "2":
            css_list = menu_select_to_delete(css_list)

        print("\nCleaned files (the original files are not changed):")
        for css_location in css_files:
            print(clean(css_location, css_list))
    else:
        print("No unused CSS elements found")


if __name__ == "__main__":
    main()
