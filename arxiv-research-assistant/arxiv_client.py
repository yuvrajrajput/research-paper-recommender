import re
from typing import Dict, List

import requests

from models import Paper


class ArxivClient:
    BASE_URL = "http://export.arxiv.org/api/query"
    USER_AGENT = "OpenClawPaperMonitor/1.0"

    def search(self, query: str, max_results: int = 20) -> List[Paper]:
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
        }
        response = requests.get(self.BASE_URL, params=params, timeout=30, headers={"User-Agent": self.USER_AGENT})
        response.raise_for_status()
        return self._parse_atom(response.text)

    def _parse_atom(self, xml_text: str) -> List[Paper]:
        import xml.etree.ElementTree as ET

        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        root = ET.fromstring(xml_text)
        papers = []

        for entry in root.findall("atom:entry", ns):
            paper_id = self._text(entry.find("atom:id", ns))
            title = self._clean_text(self._text(entry.find("atom:title", ns)))
            summary = self._clean_text(self._text(entry.find("atom:summary", ns)))
            authors = [self._text(author.find("atom:name", ns)) for author in entry.findall("atom:author", ns)]
            published = self._text(entry.find("atom:published", ns))
            updated = self._text(entry.find("atom:updated", ns))
            categories = [tag.attrib.get("term", "") for tag in entry.findall("atom:category", ns)]
            link = self._find_link(entry, ns)

            papers.append(
                Paper(
                    id=paper_id,
                    title=title,
                    summary=summary,
                    authors=authors,
                    published=published,
                    updated=updated,
                    categories=categories,
                    link=link,
                )
            )

        return papers

    def _find_link(self, entry, ns: Dict[str, str]) -> str:
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("rel") == "alternate":
                return link.attrib.get("href", "")
        return self._text(entry.find("atom:link", ns))

    def _text(self, node) -> str:
        return node.text.strip() if node is not None and node.text else ""

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
