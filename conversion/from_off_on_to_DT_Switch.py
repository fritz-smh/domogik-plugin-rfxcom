def from_DT_Switch_to_off_on(x):
    # off - on translated to 0 - 1
    if x == "off":
        return 0
    else:
        return 1

