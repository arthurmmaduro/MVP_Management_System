import re

_multiple_spaces = re.compile(r'\s+')


def normalize_spaces(value: str | None) -> str:
    """
    Normalize white spaces:
    - Convert None in ''
    - Remove spaces at begin and end
    - Colapse multiples spaces/tabs on one space
    """

    s = (value or '').strip()
    if not s:
        return ''
    return _multiple_spaces.sub(' ', s)
