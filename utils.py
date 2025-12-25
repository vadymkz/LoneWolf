import re

from settings import EXCLUDE_FROM_TITLE, EXCLUDE_FROM_COMPANY_NAME, MINIMAL_SALARY


def normalize_label(label: str) -> str:
    for symbol in ["(", ")", "[", "]"]:
        label = label.replace(symbol, "")
    label = label.replace("/", " ")
    return label


def normalize_description(desc: str) -> str:
    if desc:
        return re.sub(r"\s+", " ", desc).strip()
    return desc


def title_has_excluded_words(title: str) -> bool:
    title_words = set(normalize_label(title).lower().split())
    return bool(title_words & EXCLUDE_FROM_TITLE)


def company_has_excluded_words(company: str) -> bool:
    title_words = set(normalize_label(company).lower().split())
    return bool(title_words & EXCLUDE_FROM_COMPANY_NAME)


def is_small_salary(salary: str) -> bool:
    if not salary:
        return False
    numbers = [float(n.replace(',', '')) for n in re.findall(r'\d+\.?\d*', salary)]
    if not numbers:
        return False
    return max(numbers) < MINIMAL_SALARY
