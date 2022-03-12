class paginate():
        def __init__(self, data, length, sep = ""):
                self.sep = bytes(sep, encoding = 'utf-8')
                self.length = length - 15
                test = self.process(bytes(data, encoding = 'utf-8'))
                self.data = [str(e, encoding = 'utf-8') for e in test]

        def __getitem__(self, page = 0):
                try: res = self.data[int(page) - 1]
                except: res, page = self.data[0], 1
                finally: return res + self.suffix(page)

        def __str__(self): return self.data[0] + self.suffix[1]

        def __iter__(self):
            for i, e in enumerate(self.data): yield e + self.suffix(i + 1)

        def suffix(self, page): return (f" (page {page}/{len(self.data)})" if len(self.data) > 1 else "")

        def process(self, data):
            if len(data) <= self.length: return [data]
            else:
                spacing = len(self.sep)
                prefix = data[:self.length]
                try: cut = prefix.rindex(self.sep)
                except ValueError:
                    m, l = data, self.length
                    while l:
                        try:
                            a, b = (data[:l - 3] + b'\xe2\x80\xa6'),  data[l - 3:] #byte representation of ellipses char
                            [str(e, encoding = 'utf-8') for e in (a, b)]
                        except ValueError: l -= 1
                        else: return [a] + self.process(b)
                else: return [data[:cut]] + self.process(data[cut + spacing:])

def trim_bytes(m = "", l = 0):
    if m:
        m = bytes(m, encoding = 'utf-8')
        while m:
            try: m = str(m[:l], encoding = 'utf-8')
            except ValueError: l -= 1
            else: break
    return (m, l)

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
