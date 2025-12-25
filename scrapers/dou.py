import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

from models import Vacancy
from utils import title_has_excluded_words, company_has_excluded_words, is_small_salary
from database import get_vacancies, insert_vacancies
from logger import logger

app = FastAPI()

BASE = "https://jobs.dou.ua"
BASE_URL = f"{BASE}/vacancies/"
CATEGORY = "Python"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}?category={CATEGORY}",
    "Accept-Language": "uk, en-US;q=0.9, en;q=0.8",
    "Connection": "keep-alive"
}


def get_session_and_csrf():
    """Get a requests session and CSRF token."""
    session = requests.Session()
    resp = session.get(f"{BASE_URL}?category={CATEGORY}", headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    token_tag = soup.select_one("input[name=csrfmiddlewaretoken]")
    token = token_tag["value"] if token_tag else ""
    return session, token


def fetch_batch(session, csrf_token, count=20):
    """Fetch a single batch of vacancies via xhr-load."""
    data = {"csrfmiddlewaretoken": csrf_token, "count": count}
    resp = session.post(f"{BASE}/vacancies/xhr-load/?category={CATEGORY}", data=data, headers=HEADERS)
    if resp.status_code != 200:
        return None, False
    json_data = resp.json()
    return json_data.get("html", ""), json_data.get("last", False)


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    vacancies = []

    for v in soup.select("li.l-vacancy"):
        title_tag = v.select_one("div.title a.vt")
        if not title_tag:
            continue

        company_tag = v.select_one("div.title a.company")
        salary_tag = v.select_one("div.title span.salary")
        description_tag = v.select_one("div.sh-info")
        posted_at_tag = v.select_one("div.date")
        link = title_tag["href"].replace("?from=list_hot", "")

        vacancies.append(Vacancy(
            posted_at=posted_at_tag.get_text(strip=True) if posted_at_tag else "",
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True) if description_tag else "",
            link=link,
            company=company_tag.get_text(strip=True) if company_tag else "",
            salary=salary_tag.get_text(strip=True) if salary_tag else "",
            source="dou"
        ))

    return vacancies


def scrape_dou():
    session, csrf_token = get_session_and_csrf()

    resp = session.get(f"{BASE_URL}?category={CATEGORY}", headers=HEADERS)
    htmls = [str(BeautifulSoup(resp.text, "html.parser"))]

    count = 40
    while True:
        html, last = fetch_batch(session, csrf_token, count=count)
        count += 40
        if not html:
            break
        htmls.append(html)
        if last:
            break

    vacancies = []
    for html in htmls:
        batch = parse_html(html)
        vacancies.extend(batch)

    checked_links = {v["link"] for v in get_vacancies("dou")}
    vacancies = [v for v in vacancies if v.link not in checked_links]
    return vacancies


@app.get("/dou")
def get_dou():
    logger.info("Scraping DOU...")
    all_vacancies = scrape_dou()
    checked_links = {v["link"] for v in get_vacancies("dou")}
    new_vacancies = []
    skipped_num = 0

    for v in all_vacancies:
        if v.link in checked_links:
            continue
        if title_has_excluded_words(v.title) or company_has_excluded_words(v.company) or is_small_salary(v.salary):
            skipped_num += 1
            continue
        new_vacancies.append(v)

    if skipped_num:
        logger.info(f"Filtered total: {skipped_num}")

    if new_vacancies_num := len(new_vacancies):
        insert_vacancies(new_vacancies)
        logger.info(f"Added {new_vacancies_num} new vacancies")
    elif skipped_num:
        logger.info("No new vacancies")

    return {"stored": new_vacancies_num}


if __name__ == "__main__":
    get_dou()
