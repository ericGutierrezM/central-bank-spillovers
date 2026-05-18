from __future__ import annotations

import re
from collections import Counter
from decimal import Decimal
from fractions import Fraction


RAW_VULGAR_FRACTIONS: dict[str, Fraction | None] = {
    "¼": Fraction(1, 4),
    "½": Fraction(1, 2),
    "¾": Fraction(3, 4),
    "⅐": Fraction(1, 7),
    "⅑": Fraction(1, 9),
    "⅒": Fraction(1, 10),
    "⅓": Fraction(1, 3),
    "⅔": Fraction(2, 3),
    "⅕": Fraction(1, 5),
    "⅖": Fraction(2, 5),
    "⅗": Fraction(3, 5),
    "⅘": Fraction(4, 5),
    "⅙": Fraction(1, 6),
    "⅚": Fraction(5, 6),
    "⅛": Fraction(1, 8),
    "⅜": Fraction(3, 8),
    "⅝": Fraction(5, 8),
    "⅞": Fraction(7, 8),
    "⅟": None,
}
VULGAR_FRACTIONS = frozenset(RAW_VULGAR_FRACTIONS)
VULGAR_FRACTION_PATTERN = re.compile(
    rf"(?P<whole>\d+)?(?P<fraction>[{re.escape(''.join(VULGAR_FRACTIONS))}])"
)


def _is_terminating_decimal(denominator: int) -> bool:
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    return denominator == 1


def _strip_decimal(text: str) -> str:
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _format_fraction(value: Fraction) -> str:
    decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
    if _is_terminating_decimal(value.denominator):
        return _strip_decimal(format(decimal_value, "f"))
    return _strip_decimal(format(decimal_value.quantize(Decimal("0.0001")), "f"))


VULGAR_FRACTION_REPLACEMENTS = {
    ch: ("1/" if value is None else _format_fraction(value))
    for ch, value in RAW_VULGAR_FRACTIONS.items()
}


def count_vulgar_fractions(text: str) -> Counter[str]:
    return Counter(ch for ch in text if ch in VULGAR_FRACTIONS)


def replace_vulgar_fractions(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        whole = match.group("whole")
        fraction_char = match.group("fraction")
        fraction_value = RAW_VULGAR_FRACTIONS[fraction_char]

        if fraction_value is None:
            return f"{whole or ''}1/"
        if whole is None:
            return VULGAR_FRACTION_REPLACEMENTS[fraction_char]
        return _format_fraction(Fraction(int(whole), 1) + fraction_value)

    return VULGAR_FRACTION_PATTERN.sub(repl, text)
