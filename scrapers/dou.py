import asyncio

from main import app
from typing import List
from models import Vacancy
from base import BaseScraper
from bs4 import BeautifulSoup

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


class DOUScraper(BaseScraper):
    def __init__(self):
        super().__init__('DOU')

    @staticmethod
    async def fetch_dou_batch(session, csrf_token, sem, count=20):
        async with sem:
            await asyncio.sleep(0.7)
            data = {"csrfmiddlewaretoken": csrf_token, "count": count}
            resp = await session.post(
                f"{BASE}/vacancies/xhr-load/?category={CATEGORY}", data=data, headers=HEADERS, timeout=10
            )
            if resp.status_code != 200:
                return None, False
            json_data = resp.json()
            return json_data.get("html", "").strip(), json_data.get("last", False)

    def parse_page_to_models(self, html):
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

            vacancies.append(self.create_vacancy(
                posted_at=posted_at_tag.get_text(strip=True) if posted_at_tag else "",
                title=title_tag.get_text(strip=True),
                description=description_tag.get_text(strip=True) or "",
                link=link,
                company=company_tag.get_text(strip=True) if company_tag else "",
                salary=salary_tag.get_text(strip=True) if salary_tag else ""
            ))

        return vacancies

    async def scrape(self) -> List[Vacancy]:
        async with self.get_http_client(HEADERS) as client:
            main_page = await client.get(f"{BASE_URL}?category={CATEGORY}")
            main_page_soup = BeautifulSoup(main_page.text, 'html.parser')
            token_tag = main_page_soup.select_one("input[name=csrfmiddlewaretoken]")
            csrf_token = token_tag["value"] if token_tag else ""
            if not csrf_token:
                raise RuntimeError("DOU CSRF token not found.")

            htmls = [str(BeautifulSoup(main_page.text, "html.parser"))]
            count = 40
            batch_size = 40
            sem = asyncio.Semaphore(1)

            while True:
                tasks = [self.fetch_dou_batch(client, csrf_token, sem, count=count + batch_size * i) for i in range(2)]
                stop = False

                for task in asyncio.as_completed(tasks):
                    html, last = await task
                    if html:
                        htmls.append(html)
                    if not html or last:
                        stop = True

                count += batch_size * len(tasks)
                if stop:
                    break

        vacancies = self.htmls_to_vacancies(htmls)
        return vacancies


@app.get("/dou")
async def get_dou():
    result = await DOUScraper().save_results()
    return result


if __name__ == "__main__":
    print(asyncio.run(get_dou()))
