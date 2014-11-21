def from_DT_Switch_to_off_on(x):
    # 0 - 1 translated to off / on
    if str(x) == "0":
        return "off"
    else:
        return "on"

