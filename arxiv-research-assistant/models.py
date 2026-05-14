from dataclasses import dataclass
from typing import List


@dataclass
class Paper:
    id: str
    title: str
    summary: str
    authors: List[str]
    published: str
    updated: str
    categories: List[str]
    link: str
    score: float = 0.0
    cluster: int = -1

    def to_brief(self) -> str:
        return f"**{self.title.strip()}**\nAuthors: {', '.join(self.authors)}\nCategories: {', '.join(self.categories)}\nPublished: {self.published}\nLink: {self.link}"
