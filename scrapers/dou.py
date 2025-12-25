import requests

from fastapi import FastAPI
from bs4 import BeautifulSoup

from models import Vacancy
from utils import title_has_excluded_words
from database import get_vacancies, insert_vacancies


app = FastAPI()

BASE_URL = "https://jobs.dou.ua/vacancies/?category=Python"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


@app.get("/jobs")
def get_jobs():
    checked_vacancies_links = [v["link"] for v in get_vacancies("dou")]

    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    new_jobs = []
    vacancy_list = soup.select("ul.lt > li.l-vacancy")
    for v in vacancy_list:
        title_tag = v.select_one("div.title a.vt")
        if not title_tag:
            continue
        link = title_tag["href"].replace("?from=list_hot", "")
        if link in checked_vacancies_links:
            continue
        title = title_tag.get_text(strip=True)
        if title_has_excluded_words(title):
            continue

        company_tag = v.select_one("div.title a.company")
        salary_tag = v.select_one("div.title span.salary")
        description_tag = v.select_one("div.sh-info")
        posted_at = v.select_one("div.date")

        new_jobs.append(Vacancy(
            posted_at=posted_at.get_text(strip=True) if posted_at else "",
            title=title,
            description=description_tag.get_text(strip=True) if description_tag else "",
            link=link,
            company=company_tag.get_text(strip=True) if company_tag else "",
            salary=salary_tag.get_text(strip=True) if salary_tag else "",
            source="dou",
        ))

    insert_vacancies(new_jobs)


get_jobs()
