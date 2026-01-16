import os


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("cp1251").decode("utf-8")
    except UnicodeError:
        return s


def get_list_env_var(env_name: str) -> list:
    raw = fix_mojibake(os.getenv(env_name, "")).split(",")
    return [v.strip().casefold() for v in raw if v]


def get_int_env(name: str, default: int | None = None) -> int:
    value = os.getenv(name)
    if value is None:
        if default is None:
            raise RuntimeError(f"Missing env var: {name}")
        return default
    return int(value)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_FROM_TITLE = set(get_list_env_var("EXCLUDE_FROM_TITLE"))
EXCLUDE_FROM_COMPANY_NAME = set(get_list_env_var("EXCLUDE_FROM_COMPANY_NAME"))

MINIMAL_SALARY = get_int_env("MIN_SALARY", 0)
MAX_SALARY = get_int_env("MAX_SALARY", 8000)

DJINNI_LOGIN = os.getenv("DJINNI_LOGIN")
DJINNI_PASSWORD = os.getenv("DJINNI_PASSWORD")
