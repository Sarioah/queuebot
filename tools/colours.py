def colourise(string, colour):
    c = {
    "WHITE"  : "\033[0m",
    "GREY"   : "\033[30;1m",
    "RED"    : "\033[31;1m",
    "GREEN"  : "\033[32;1m",
    "YELLOW" : "\033[33;1m",
    "BLUE"   : "\033[34;1m",
    "PURPLE" : "\033[35;1m",
    "CYAN"   : "\033[36;1m"}

    try: return(f"{c[colour]}{string}{c['WHITE']}")
    except KeyError: raise KeyError(f"Colour \"{colour}\" invalid")