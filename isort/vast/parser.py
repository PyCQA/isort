"""Defines isort's Very Abstract Syntax Tree code parser implementation."""


class Parser(object):
    """Defines the direct interaction between jiphy and the file content"""
    __slots__ = (index, code, output)

    def __init__(self, code):
        self.index = 0
        self.code = code
        self.output = []

    def text_till(self, strings, keep_index=False):
        """Returns all text till it encounters the given string (or one of the given strings)"""
        if isinstance(strings, str):
            strings = [strings]

        original_index = self.index

        text = ""
        matched_string = ""

        while self.more:
            test_against = self.characters(len(max(strings, key=len)))
            for string in strings:
                if string.startswith("^"):
                    if test_against[0] in (" ", "\t", "\n", ")", "(") and test_against[1:].startswith(string[1:]):
                        matched_string = string
                        break
                if test_against.startswith(string):
                    matched_string = string
                    break

            if matched_string:
                break

            text += self.pop()

        self += 1

        if keep_index:
            self.index = original_index

        return (text, matched_string)

    def __getitem__(self, index):
        return self.code[index]

    def text_after(self, start, match_on):
        """Returns all text till it encounters the given string (or one of the given strings)"""
        text = ""
        index = start - 1
        while index > 0:
            text = self.code[index:start]
            if text.startswith(match_on):
                return text.lstrip(match_on)
            index -= 1

        return text.lstrip(match_on)

    def pop(self):
        """removes the current character then moves to the next one, returning the current character"""
        char = self.code[self.index]
        self.index += 1
        return char

    def characters(self, numberOfCharacters):
        """Returns characters at index + number of characters"""
        return self.code[self.index:self.index + numberOfCharacters]

    def __iadd__(self, other):
        self.index += other
        return self

    def __isub__(self, other):
        self.index -= other
        return self

    @property
    def more(self):
        """Returns true if there is more code to parse"""
        return self.index < len(self)

    def __len__(self):
        return len(self.code)

    def behind(self, start, difference):
        """Returns the specified number of characters behind 'start'"""
        return self.code[start - difference: start]

    def ahead(self, start, difference):
        """Returns the specified number of characters in front of 'start'"""
        return self.code[start: start + difference]

    def next_content(self, start, amount=1):
        """Returns the next non-whitespace characters"""
        while start < len(self.code) and self.code[start] in (' ', '\t', '\n'):
            start += 1

        return self.code[start: start + amount]

    def prev_content(self, start, amount=1):
        """Returns the prev non-whitespace characters"""
        while start > 0 and self.code[start] in (' ', '\t', '\n'):
            start -= 1

        return self.code[(start or amount) - amount: start]

    def __str__(self):
        return "".join(self.output)
