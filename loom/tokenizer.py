import nltk
import re

# This Tokenizer is heavily based on the NLTK Penn Treebank Tokenizer:
#  https://github.com/nltk/nltk/blob/develop/nltk/tokenize/treebank.py


class LoomTokenizer:
    """
    This tokenizer is designed to split words and punctuation, but it does not separate words into semantic units like
    the original Treebank tokenizer on which it is based.
    """
    STARTING_QUOTES = [
        (re.compile(r'^\"'), r'" '),                                    # |"Blah blah"|         -> |" Blah blah"|
        (re.compile(r'^\''), r"' "),                                    # |'Blah blah'|         -> |' Blah blah'|
        (re.compile(r'([ (\[{<])"'), r'\1 " '),                         # |Blah "blah" blah.|   -> |Blah " blah" blah.|
        (re.compile(r'([ (\[{<])\''), r"\1 ' "),                        # |Blah 'blah' blah.|   -> |Blah ' blah' blah.|
    ]

    ENDING_QUOTES = [
        (re.compile(r'"'), ' " '),                                      # |Blah " blah" blah.|  -> |Blah " blah " blah.|
        (re.compile(r"([^' ])('[sS]|') "), r"\1 \2 "),                  # |Blah's blah.|        -> |Blah 's blah.|
        # (re.compile(r'\' '), ' \' '),                                   # |Blah ' blah'.|     -> |Blah ' blah '.|
    ]

    PUNCTUATION = [
        (re.compile(r'([:,])([^\d])'), r' \1 \2'),                      # |Blah: blah.|         -> |Blah : blah.|
        (re.compile(r'([:,])$'), r' \1 '),                              # |Blah:|               -> |Blah : |
        (re.compile(r'\.\.\.'), r' ... '),                              # |Blah...blah.|        -> |Blah ... blah.|
        (re.compile(r'[;@#$%&]'), r' \g<0> '),
        (re.compile(r'([^.])(\.)([\])}>"\']*)\s*$'), r'\1 \2\3 '),      # |(Blah.)   |          -> |(Blah .) |
        (re.compile(r'[?!]'), r' \g<0> '),
        (re.compile(r"([^'])' "), r"\1 ' "),                            # |'Blah blah' blah.|   -> |'Blah blah ' blah.|
    ]

    PARENS_BRACKETS = [
        (re.compile(r'[\]\[(){\}<>]'), r' \g<0> '),
        (re.compile(r'--'), r' -- '),                                   # |Blah--blah|          -> |Blah -- blah|
    ]

    @classmethod
    def word_tokenize(cls, text):
        for regexp, substitution in cls.STARTING_QUOTES:
            text = regexp.sub(substitution, text)
        for regexp, substitution in cls.PUNCTUATION:
            text = regexp.sub(substitution, text)
        for regexp, substitution in cls.PARENS_BRACKETS:
            text = regexp.sub(substitution, text)
        text = " " + text + " "
        for regexp, substitution in cls.ENDING_QUOTES:
            text = regexp.sub(substitution, text)
        return text.split()

    @classmethod
    def sent_tokenize(cls, text):
        return nltk.sent_tokenize(text)
