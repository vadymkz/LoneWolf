import asyncio

from fastapi import FastAPI
from database import create_tables
from scrapers.dou import DOUScraper
from scrapers.djinni import DjinniScraper
from contextlib import asynccontextmanager

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await create_tables()
    yield


@app.get("/dou")
async def get_dou():
    result = await DOUScraper().run()
    return result


@app.get("/djinni")
async def get_djinni():
    result = await DjinniScraper().run()
    return result


@app.get("/scrape")
async def scrape():
    djinni_result, dou_result = await asyncio.gather(
        DjinniScraper().run(),
        DOUScraper().run(),
    )
    return {
        "djinni": djinni_result,
        "dou": dou_result,
    }


if __name__ == "__main__":
    print(asyncio.run(scrape()))
