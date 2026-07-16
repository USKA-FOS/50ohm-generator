import re

from mistletoe.span_token import SpanToken


class Section(SpanToken):
    """
    Resolve references to other section
    Identifies "[sec:$]"
    This is umstritten but useful for linking if used reasonably
    """

    pattern = re.compile(r"\[sec\:(\S+)\]")

    def __init__(self, match_object):
        self.first = match_object.group(1)
