class paginate():

    def __init__(self, data, length, sep=""):
        self.sep = bytes(sep, encoding='utf-8')
        self.length = length - 15
        test = self.process(bytes(data, encoding='utf-8'))
        self.data = [
            str(e, encoding='utf-8')
            for e in test
            ]

    def __getitem__(self, page=0):
        try:
            res = self.data[int(page) - 1]
        except Exception:
            res, page = self.data[0], 1
        finally:
            return res + self.suffix(page)

    def __str__(self):
        return self.data[0] + self.suffix[1]

    def __iter__(self):
        for i, e in enumerate(self.data):
            yield e + self.suffix(i + 1)

    def suffix(self, page):
        if len(self.data) > 1:
            return f" (page {page}/{len(self.data)})"
        else:
            return ""

    def process(self, data):
        if len(data) <= self.length:
            return [data]
        else:
            spacing = len(self.sep)
            prefix = data[:self.length]
            try:
                cut = prefix.rindex(self.sep)
            except ValueError:
                L = self.length
                while L:
                    try:
                        # byte representation of ellipses char
                        a = (data[:L - 3] + b'\xe2\x80\xa6')
                        b = data[L - 3:]
                        [str(e, encoding='utf-8') for e in (a, b)]
                    except ValueError:
                        L -= 1
                    else:
                        return [a] + self.process(b)
            else:
                return [data[:cut]] + self.process(data[cut + spacing:])


def trim_bytes(m="", L=0):
    if m:
        m = bytes(m, encoding='utf-8')
        while m:
            try:
                m = str(m[:L], encoding='utf-8')
            except ValueError:
                L -= 1
            else:
                break
    return (m, L)


def colourise(string, colour):
    c = {
        "WHITE"  : "\033[0m",
        "GREY"   : "\033[30;1m",
        "RED"    : "\033[31;1m",
        "GREEN"  : "\033[32;1m",
        "YELLOW" : "\033[33;1m",
        "BLUE"   : "\033[34;1m",
        "PURPLE" : "\033[35;1m",
        "CYAN"   : "\033[36;1m"
        }

    try:
        if string:
            string = string.replace("\33[0m", c[colour])
        return (
            f"{c[colour]}"
            f"{string}"
            f"{c['WHITE']}"
            )
    except KeyError:
        raise KeyError(f"Colour \"{colour}\" invalid")
