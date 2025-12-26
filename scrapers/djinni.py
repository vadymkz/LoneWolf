import httpx
import asyncio

from bs4 import BeautifulSoup
from main import app
from models import Vacancy
from typing import List
from logger import logger, log_scraper_results
from database import get_vacancies, insert_vacancies
from utils import title_has_excluded_words, is_high_salary, is_small_salary, company_has_excluded_words
from settings import DJINNI_LOGIN, DJINNI_PASSWORD

LOGIN_URL = "https://djinni.co/login"
BASE_JOBS_URL = "https://djinni.co/jobs/?primary_keyword=Python&salary=3000&employment=remote&company_type=product"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


async def get_total_pages(html_content: str) -> int:
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination = soup.find('ul', class_='pagination')
    if not pagination:
        return 1

    page_links = pagination.find_all('a', class_='page-link')
    pages = []
    for link in page_links:
        text = link.get_text(strip=True)
        if text.isdigit():
            pages.append(int(text))
    return max(pages) if pages else 1


async def parse_page_to_models(html_content: str) -> List[Vacancy]:
    soup = BeautifulSoup(html_content, 'html.parser')
    vacancies = []

    items = soup.find_all('li', class_=['list-jobs__item', 'mb-4'])

    for item in items:
        title_tag = item.find('a', class_='job-item__title-link')
        if not title_tag:
            continue

        company_tag = item.find('a', attrs={"data-analytics": "company_page"})
        company_name = company_tag.get_text(strip=True) if company_tag else ""

        salary_tag = item.find('span', class_='text-success text-nowrap')
        salary_text = salary_tag.get_text(strip=True) if salary_tag else ""

        desc_tag = item.find('span', class_='js-truncated-text')
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        time_tag = item.select_one('.text-secondary .text-nowrap:last-child')
        posted_at = time_tag.get_text(strip=True) if time_tag else ""

        vacancy = Vacancy(
            posted_at=posted_at,
            title=title_tag.get_text(strip=True),
            description=description,
            link="https://djinni.co" + title_tag['href'],
            company=company_name,
            source="djinni",
            salary=salary_text
        )
        vacancies.append(vacancy)

    return vacancies


async def scrape_djinni():
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0, headers=HEADERS) as client:
        login_page = await client.get(LOGIN_URL)
        login_soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = login_soup.find('input', dict(name='csrfmiddlewaretoken'))['value']

        await client.post(LOGIN_URL, data={
            "email": DJINNI_LOGIN,
            "password": DJINNI_PASSWORD,
            "csrfmiddlewaretoken": csrf_token
        }, headers={"Referer": LOGIN_URL})

        first_page_resp = await client.get(BASE_JOBS_URL)
        total_pages = await get_total_pages(first_page_resp.text)

        htmls = [first_page_resp.text]
        if total_pages > 1:
            for page_num in range(2, total_pages + 1):
                await asyncio.sleep(0.7)
                page_resp = await client.get(f"{BASE_JOBS_URL}&page={page_num}")
                htmls.append(page_resp.text)

    vacancies = []
    for html in htmls:
        vacancies.extend(await parse_page_to_models(html))
    return vacancies


@app.get("/djinni", response_model=List[Vacancy])
async def get_djinni():
    logger.info("Scraping Djinni...")
    all_vacancies = await scrape_djinni()
    checked_links = {v["link"] for v in get_vacancies("djinni")}
    new_vacancies = []
    skipped_num = 0

    for v in all_vacancies:
        if v.link in checked_links:
            continue
        if (
            title_has_excluded_words(v.title) or
            company_has_excluded_words(v.company) or
            is_small_salary(v.salary) or
            is_high_salary(v.salary)
        ):
            skipped_num += 1
            continue
        new_vacancies.append(v)

    if new_vacancies_num := len(new_vacancies):
        insert_vacancies(new_vacancies)

    log_scraper_results(skipped_num, new_vacancies_num)

    return {"stored": new_vacancies_num}


if __name__ == "__main__":
    data = asyncio.run(get_djinni())
    print(data)
