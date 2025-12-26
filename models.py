from pydantic import BaseModel


class Vacancy(BaseModel):
    posted_at: str
    title: str
    description: str
    link: str
    company: str
    source: str
    salary: str
    checked: int = 0

    def to_tuple(self):
        """Return a tuple in the order expected for executemany."""
        return (
            self.posted_at,
            self.title,
            self.description,
            self.link,
            self.company,
            self.source,
            self.salary,
            self.checked,
        )
