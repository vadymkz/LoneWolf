import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("app_logger")


def log_scraper_results(skipped_num, new_vacancies_num):
    if skipped_num:
        logger.info(f"Filtered total: {skipped_num}")
    if new_vacancies_num := new_vacancies_num:
        logger.info(f"Added {new_vacancies_num} new vacancies")
    elif skipped_num:
        logger.info("No new vacancies")
