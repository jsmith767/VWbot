import itertools
from datetime import datetime
from typing import List, Any, Dict

from EmberEventBot.exceptions import EventIdError
from EmberEventBot.constants import Font

def txtwrap(new:str, txt: str, count:int = 1) -> str:
    """
    args:
        new: new character(s) to wrap
        txt: the text to be wrapped
        count: optional multiplier
    """
    p = new * count
    return p + txt + p

def star(i: int) -> str:
    if i == 0:
        return "*"
    return str(i)

def heading(txt: str) -> str:
    """Decorates text with: ───── ❝ Your Text Here ❞ ─────"""
    return f"───── ❝ {txt} ❞ ─────"

def bubble(txt: str) -> str:
    """Makes a text art bubble around text"""
    bubble_len = len(txt) + 6
    txt = negative_circled_latin(txt=txt)
    return f"╭{'─' * bubble_len}╮\n│ {txt}\n╰{'─' * bubble_len}╯\n"

def generate_font_lookup(
    key:int=Font.LATIN.value,
    value:int=Font.NEGATIVE_SQUARED_LATIN.value,
    length = 26,
    ) -> Dict[str,str]:
    """
    Uses unicode codepoint offset to generate a lookup dictionary
    key: the int value of the first letter in your base set (A,a)
    value: the int value of the first letter in desired set (𝓐,𝕒)
    """
    d = {}
    for x in range(length):
        d[chr(key+x)] = chr(value+x)
    return d

def translate(txt:str, font_lookup:Dict) -> str:
    """
    translates txt into fun fonts using a font lookup dict
    """
    result = ""
    for x in txt:
        result += font_lookup.get(x,x)
    return result

def negative_circled_latin(txt: str) -> str:
    d = generate_font_lookup(
        key=Font.LATIN.value,
        value=Font.NEGATIVE_CIRCLED_LATIN.value,
        )
    return translate(txt=txt.upper(), font_lookup=d)


def event_idx(event_id, events: List[Any]) -> int:
    """Gets the event index in the list of events, throws EventIdError if not found."""
    # noinspection PyBroadException
    try:
        return [x['id'] for x in events].index(event_id)
    except Exception as _:
        pass
    raise EventIdError(f"Unknown event id: {event_id}")


def event_id_exists(event_id, events: List[Any]) -> bool:
    """Checks if event id is in the list of events"""
    try:
        event_idx(event_id, events)
        return True
    except EventIdError as _:
        pass
    return False


MONTH_FORMATS = ['%m', '%-m', '%b', '%B']
DAY_FORMATS = ['%d', '%-d']
YEAR_FORMATS = ['%y', '%-y', '%Y']
DATE_DELIMITERS = ['/', '-', ' ']
COMPUTED_FORMATS = [delimiter.join(combined) for delimiter in DATE_DELIMITERS for combined in
                    itertools.product(MONTH_FORMATS, DAY_FORMATS, YEAR_FORMATS)]
ALL_FORMATS = COMPUTED_FORMATS + ['%Y%m%d']


def munge_date(date_string: str):
    for fmt in ALL_FORMATS:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    else:
        return None
