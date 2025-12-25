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

    def to_dict(self) -> dict:
        return {
            "posted_at": self.posted_at,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "company": self.company,
            "source": self.source,
            "salary": self.salary,
            "checked": self.checked
        }

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
