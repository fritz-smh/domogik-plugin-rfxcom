def from_off_on_to_DT_Switch(x):
    # off - on translated to 0 - 1
    if x == "off":
        return 0
    else:
        return 1

