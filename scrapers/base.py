import httpx
import asyncio

from typing import List
from models import Vacancy
from abc import ABC, abstractmethod
from logger import logger, log_scraper_results
from database import get_vacancies, insert_vacancies
from utils import (
    title_has_excluded_words, is_high_salary, is_small_salary, company_has_excluded_words, normalize_description
)


class BaseScraper(ABC):
    def __init__(self, source):
        self.source: str = source
        logger.info(f"Scraping {self.source.capitalize()}...")

    @abstractmethod
    async def scrape(self) -> List[Vacancy]:
        pass

    @abstractmethod
    def parse_page_to_models(self, html: str) -> List[Vacancy]:
        pass

    @staticmethod
    def get_http_client(headers: dict) -> httpx.AsyncClient:
        return httpx.AsyncClient(follow_redirects=True, timeout=5.0, headers=headers)

    def create_vacancy(
        self,
        posted_at: str,
        title: str,
        description: str,
        link: str,
        company: str,
        salary: str
    ):
        vacancy = Vacancy(
            posted_at=posted_at,
            title=title,
            description=normalize_description(description),
            link=link,
            company=company,
            source=self.source.lower(),
            salary=normalize_description(salary)
        )
        return vacancy

    def htmls_to_vacancies(self, htmls) -> List[Vacancy]:
        if not htmls:
            return []
        return [v for html in htmls for v in self.parse_page_to_models(html)]

    @staticmethod
    async def fetch_with_pause(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore) -> str:
        async with sem:
            await asyncio.sleep(0.7)
            resp = await client.get(url)
            return resp.text

    async def run(self) -> dict:
        all_vacancies = await self.scrape()
        checked_links = {v["link"] for v in await get_vacancies(self.source.lower())}
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
            await insert_vacancies(new_vacancies)

        log_scraper_results(skipped_num, new_vacancies_num)

        return {"stored": new_vacancies_num}
