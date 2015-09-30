def from_off_on_to_DT_OpenClose(x):
    # off - on translated to 1 (close) - 0 (open)
    # the close/open sensor works as a off/on switch command
    if x == "off":
        return 1
    else:
        return 0

