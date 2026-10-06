import json
from config import RANGES_FILE


def digit_count(value):
    return len(str(value))


def load_file_groups():
    with open(RANGES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    files = data["files"]

    group_10 = []
    group_13 = []
    group_mix = []

    for item in files:
        first_len = digit_count(item["first"])
        last_len = digit_count(item["last"])

        # First aur last dono exactly 10 digit
        if first_len == 10 and last_len == 10:
            group_10.append(item)

        # First aur last dono exactly 13 digit
        elif first_len == 13 and last_len == 13:
            group_13.append(item)

        # Baaki sab Mix
        else:
            group_mix.append(item)

    return {
        "10_digit": group_10,
        "13_digit": group_13,
        "mix": group_mix,
    }
