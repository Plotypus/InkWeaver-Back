import re

# This Tokenizer is heavily based on the NLTK Penn Treebank Tokenizer:
#  https://github.com/nltk/nltk/blob/develop/nltk/tokenize/treebank.py


class Tokenizer:
    """
    This tokenizer is designed to split words and punctuation, but it does not separate words into semantic units like
    the original Treebank tokenizer on which it is based.
    """
    STARTING_QUOTES = [
        (re.compile(r'^\"'), r'" '),                                    # |"Blah blah"| -> |" Blah blah"|
        (re.compile(r'^\''), r"' "),                                    # |'Blah blah'| -> |' Blah blah'|
        (re.compile(r'([ (\[{<])"'), r'\1 " '),                         # |Blah "blah" blah.| -> |Blah " blah" blah.|
        (re.compile(r'([ (\[{<])\''), r"\1 ' "),                        # |Blah 'blah' blah.| -> |Blah ' blah' blah.|
    ]

    ENDING_QUOTES = [
        (re.compile(r'"'), ' " '),                                      # |Blah " blah" blah.| -> |Blah " blah " blah.|
        # (re.compile(r'\' '), ' \' '),                                   # |Blah ' blah'.| -> |Blah ' blah '.|
    ]

    PUNCTUATION = [
        (re.compile(r'([:,])([^\d])'), r' \1 \2'),                      # |Blah: blah.| -> |Blah : blah.|
        (re.compile(r'([:,])$'), r' \1 '),                              # |Blah:| -> |Blah : |
        (re.compile(r'\.\.\.'), r' ... '),                              # |Blah...blah.| -> |Blah ... blah.|
        (re.compile(r'[;@#$%&]'), r' \g<0> '),                          #
        (re.compile(r'([^.])(\.)([\])}>"\']*)\s*$'), r'\1 \2\3 '),    # |(Blah.)   | -> |(Blah .) |
        (re.compile(r'[?!]'), r' \g<0> '),                              #
        (re.compile(r"([^'])' "), r"\1 ' "),                            # |'Blah blah' blah.| -> |'Blah blah ' blah.|
    ]

    PARENS_BRACKETS = [
        (re.compile(r'[\]\[(){\}<>]'), r' \g<0> '),                #
        (re.compile(r'--'), r' -- '),                                   # |Blah--blah| -> |Blah -- blah|
    ]

    def tokenize(self, text):
        for regexp, substitution in self.STARTING_QUOTES:
            text = regexp.sub(substitution, text)
        for regexp, substitution in self.PUNCTUATION:
            text = regexp.sub(substitution, text)
        for regexp, substitution in self.PARENS_BRACKETS:
            text = regexp.sub(substitution, text)
        text = " " + text + " "
        for regexp, substitution in self.ENDING_QUOTES:
            text = regexp.sub(substitution, text)
        return text.split()
