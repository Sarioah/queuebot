"""
Tools for formatting / manipulating text

Classes:
    Paginate: Takes a string and returns a list of strings split to the specified
              length. Optionally attempts to cut a the specified separator where possible

Functions:
    trim_bytes: Takes a string and splits it to the specified number of bytes.
    colourise: Takes a string and a colour, returns the string with ANSI colour codes around it
"""


class Paginate:
    """
    Hold a long string and break it up into more manageable pages.

    Supports indexing to return the given page number, or iterating through all pages
    """
    def __init__(self, data, length, sep=""):
        self.sep = bytes(sep, encoding='utf-8')
        self.max_length = length - 15
        bytes_ = self.process(bytes(data, encoding='utf-8'))
        self.data = [
            str(page, encoding='utf-8')
            for page in bytes_
        ]

    def __getitem__(self, page_num=0):
        try:
            res = self.data[int(page_num) - 1]
        except Exception:
            res, page_num = self.data[0], 1
        return res + self.suffix(page_num)

    def __str__(self):
        return self.data[0] + self.suffix(1)

    def __iter__(self):
        for i, page in enumerate(self.data):
            yield page + self.suffix(i + 1)

    def suffix(self, page_num):
        """Return the specified page of data, suffixed with the page number"""
        if len(self.data) > 1:
            return f" (page {page_num}/{len(self.data)})"
        return ""

    def process(self, data):
        """
        Process the given data into groupings of bytes

        Arguments:
            data: String of bytes

        Returns:
            List of strings of bytes
        """
        if len(data) <= self.max_length:
            return [data]
        spacing = len(self.sep)
        prefix = data[:self.max_length]
        try:
            cut = prefix.rindex(self.sep)
        except ValueError:
            current_length = self.max_length
            while current_length:
                try:
                    # byte representation of ellipses char
                    front = (data[:current_length - 3] + b'\xe2\x80\xa6')
                    back = data[current_length - 3:]
                    _ = [str(e, encoding='utf-8') for e in (front, back)]
                except ValueError:
                    current_length -= 1
                else:
                    return [front] + self.process(back)
        else:
            return [data[:cut]] + self.process(data[cut + spacing:])


def trim_bytes(msg="", length=0):
    """
    Trim a string to the specified number of bytes

    Arguments:
        msg: Input string
        length: Length to trim the input string to

    Returns:
        Trimmed version of the input string
    """
    if msg:
        msg = bytes(msg, encoding='utf-8')
        while msg:
            try:
                msg = str(msg[:length], encoding='utf-8')
            except ValueError:
                length -= 1
            else:
                break
    return (msg, length)


def colourise(string, colour):
    """
    Take a string and surround it with ANSI colour formatting codes

    Arguments:
        string: Input string
        colour: Colour to format the input string with

    Returns:
        Formatted version of the input string
    """
    colours = {
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
            string = string.replace("\33[0m", colours[colour])
        return (
            f"{colours[colour]}"
            f"{string}"
            f"{colours['WHITE']}"
        )
    except KeyError as exc:
        raise KeyError(f"Colour \"{colour}\" invalid") from exc
