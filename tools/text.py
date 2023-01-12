"""Tools for formatting / manipulating text.

Classes:
    Paginate: Takes a string and returns a list of strings split to the
        specified length. Optionally attempts to cut at the specified separator
        where possible.

Functions:
    trim_bytes: Take a string and splits it to the specified number of bytes.
    colourise: Take a string and a colour, returns the string with ANSI colour
        codes around it.
"""


ENCODING = "UTF-8"


class Paginate:
    """Hold a long string and break it up into more manageable pages.

    Supports indexing to return the given page number,
    or iterating through all pages.
    """

    def __init__(self, data, length, sep=""):
        """Create the Paginate.

        Args:
            data: Input string that may need to be broken up.
            length: Maximum page length in bytes.
            sep: Optional separator string. When breaking data into pages, we
                will attempt to break near where these strings appear.
        """
        self.sep = to_bytes(sep)
        bytes_, self.max_length = self._process_data(data, length)
        self.data = [to_string(page) for page in bytes_]

    def __getitem__(self, page_num=0):
        """Redirect subscript accesses to the paginated data.

        Args:
            page_num: Page of data to request, starts at 1.

        Returns:
            String of data contained in the requested page.
        """
        try:
            page_num = int(page_num)
            page_number = page_num - 1 if page_num > 0 else page_num
            res = self.data[page_number]
        except Exception:
            res = self.data[0]
        return res

    def __str__(self):
        """Return the first page of data, formatted as string."""
        return self.data[0]

    def __iter__(self):
        """Iterate over the data pages."""
        return iter(self.data)

    def _add_suffixes(self, data):
        """Append page suffixes to each element of the given sequence."""
        length = len(data)
        if length <= 1:
            return data
        return [
            to_bytes(f"{to_string(string)} (page {index + 1}/{length})")
            for index, string in enumerate(data)
        ]

    def _split_bytes(self, data, max_length):
        """Process the given data into groupings of bytes.

        Args:
            data: String of bytes.
            max_length: Maximum length that the byte strings are split into.

        Returns:
            List of byte strings.
        """
        if len(data) <= max_length:
            return [data]
        spacing = len(self.sep)
        prefix = data[:max_length]
        try:
            cut = prefix.rindex(self.sep)
            _ = str(prefix, encoding="utf-8")
        except ValueError:
            current_length = max_length
            while current_length:
                try:
                    # byte representation of ellipses char
                    front = data[: current_length - 3] + b"\xe2\x80\xa6"
                    back = data[current_length - 3 :]
                    _ = [str(e, encoding="utf-8") for e in (front, back)]
                except ValueError:
                    current_length -= 1
                else:
                    return [front] + self._split_bytes(back, max_length)
        else:
            return [data[:cut]] + self._split_bytes(data[cut + spacing :], max_length)

    def _process_data(self, data, max_length):
        """Take a given string and split it into smaller pages.

        Args:
            data: Input string to split up.
            max_length: Maximum byte length of each page.

        Returns:
            List of byte strings representing the pages. May be a list
            containing a single empty string if there was a problem splitting
            the input string.
        """
        data = to_bytes(data)
        for length in range(max_length, 1, -1):
            try:
                output = self._split_bytes(data, length)
            except RecursionError:
                output = [b""]
            output = self._add_suffixes(output)
            if all(len(string) < max_length for string in output):
                return output, length
        return [b""], 1


def to_bytes(data):
    """Convert the given string into byte representation."""
    try:
        return data.encode(ENCODING)
    except AttributeError:
        return b""


def to_string(data):
    """Convert the given byte sequence into string representation."""
    try:
        return data.decode(ENCODING)
    except AttributeError:
        return ""


def trim_bytes(msg="", length=0):
    """Trim a string to the specified number of bytes.

    Args:
        msg: Input string
        length: Length to trim the input string to

    Returns:
        Trimmed version of the input string
    """
    if msg:
        msg = to_bytes(msg)
        while msg:
            try:
                msg = to_string(msg[:length])
            except ValueError:
                length -= 1
            else:
                # prevent optimisers from skipping this line and messing up
                # coverage reporting using a useless function call
                len("1")
                break
    return (msg, length)


def colourise(string, colour):
    """Take a string and surround it with ANSI colour formatting codes.

    Args:
        string: Input string.
        colour: Colour to format the input string with.

    Returns:
        Formatted version of the input string.

    Raises:
        KeyError: If an invalid colour is specified.
    """
    colours = {
        "WHITE": "\033[0m",
        "GREY": "\033[30;1m",
        "RED": "\033[31;1m",
        "GREEN": "\033[32;1m",
        "YELLOW": "\033[33;1m",
        "BLUE": "\033[34;1m",
        "PURPLE": "\033[35;1m",
        "CYAN": "\033[36;1m",
    }

    try:
        if string:
            string = string.replace("\33[0m", colours[colour])
        return f"{colours[colour]}{string}{colours['WHITE']}"
    except KeyError as exc:
        raise KeyError(f'Colour "{colour}" invalid') from exc
