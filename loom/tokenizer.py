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

    @staticmethod
    def word_tokenize(text):
        for regexp, substitution in LoomTokenizer.STARTING_QUOTES:
            text = regexp.sub(substitution, text)
        for regexp, substitution in LoomTokenizer.PUNCTUATION:
            text = regexp.sub(substitution, text)
        for regexp, substitution in LoomTokenizer.PARENS_BRACKETS:
            text = regexp.sub(substitution, text)
        text = " " + text + " "
        for regexp, substitution in LoomTokenizer.ENDING_QUOTES:
            text = regexp.sub(substitution, text)
        return text.split()

    @staticmethod
    def sent_tokenize(text):
        return nltk.sent_tokenize(text)
