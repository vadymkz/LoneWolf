import asyncio

from typing import List
from models import Vacancy
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils import normalize_description
from settings import DJINNI_LOGIN, DJINNI_PASSWORD

LOGIN_URL = "https://djinni.co/login"
BASE_JOBS_URL = ("https://djinni.co/jobs/?primary_keyword="
                 "Python&salary=3000&employment=remote&company_type=product&region=UKR")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


class DjinniScraper(BaseScraper):
    def __init__(self):
        super().__init__('Djinni')

    @staticmethod
    def get_total_pages(html_content: str) -> int:
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

    def parse_page_to_models(self, html_content: str) -> List[Vacancy]:
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

            vacancies.append(self.create_vacancy(
                posted_at=posted_at,
                title=title_tag.get_text(strip=True),
                description=normalize_description(description),
                link="https://djinni.co" + title_tag['href'],
                company=company_name,
                salary=salary_text
            ))

        return vacancies

    async def scrape(self) -> List[Vacancy]:
        async with self.get_http_client(HEADERS) as client:
            login_page = await client.get(LOGIN_URL)
            login_soup = BeautifulSoup(login_page.text, 'html.parser')
            csrf_token = login_soup.find('input', dict(name='csrfmiddlewaretoken'))['value']

            await client.post(LOGIN_URL, data={
                "email": DJINNI_LOGIN,
                "password": DJINNI_PASSWORD,
                "csrfmiddlewaretoken": csrf_token
            }, headers={"Referer": LOGIN_URL})

            first_page_resp = await client.get(BASE_JOBS_URL)
            total_pages = self.get_total_pages(first_page_resp.text)

            htmls = [first_page_resp.text]
            if total_pages > 1:
                sem = asyncio.Semaphore(1)
                htmls.extend(await asyncio.gather(*[
                    self.fetch_with_pause(client, f"{BASE_JOBS_URL}&page={page_num}", sem)
                    for page_num in range(2, total_pages + 1)
                ]))

        vacancies = self.htmls_to_vacancies(htmls)
        return vacancies


if __name__ == "__main__":
    async def get_djinni():
        return await DjinniScraper().run()
    print(asyncio.run(get_djinni()))
