def get_value(css):
    value = css["value"]
    if css["type"] == "class":
        value = "." + value
    elif css["type"] == "id":
        value = "#" + value
    return value
