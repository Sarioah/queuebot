class colours():
    WHITE  = "\033[0m"
    GREY   = "\033[30;1m"
    RED    = "\033[31;1m"
    GREEN  = "\033[32;1m"
    YELLOW = "\033[33;1m"
    BLUE   = "\033[34;1m"
    PURPLE = "\033[35;1m"
    CYAN   = "\033[36;1m"

    def __call__(self, string, colour):
        try: return(f"{getattr(self, colour)}{string}{self.WHITE}")
        except AttributeError: raise AttributeError(f"Colour \"{colour}\" invalid")
