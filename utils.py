from settings import EXCLUDE_FROM_TITLE


def title_has_excluded_words(title: str) -> bool:
    for symbol in ["(", ")", "[", "]"]:
        title = title.replace(symbol, "")
    title_words = set(title.lower().split())
    return bool(title_words & EXCLUDE_FROM_TITLE)
