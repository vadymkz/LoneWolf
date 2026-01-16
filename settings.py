import os


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("cp1251").decode("utf-8")
    except UnicodeError:
        return s


def get_list_env_var(env_name: str) -> list:
    raw = fix_mojibake(os.getenv(env_name, "")).split(",")
    return [v.strip().casefold().lower() for v in raw if v]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_FROM_TITLE = set(get_list_env_var("EXCLUDE_FROM_TITLE"))
EXCLUDE_FROM_COMPANY_NAME = set(get_list_env_var("EXCLUDE_FROM_COMPANY_NAME"))

MINIMAL_SALARY = int(os.getenv("MIN_SALARY"))
MAX_SALARY = int(os.getenv("MAX_SALARY"))

DJINNI_LOGIN = os.getenv("DJINNI_LOGIN")
DJINNI_PASSWORD = os.getenv("DJINNI_PASSWORD")
