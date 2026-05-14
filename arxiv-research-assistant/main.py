import json
import logging
import os
import time
from typing import Dict, List

import yaml

from arxiv_client import ArxivClient
from models import Paper
from notifier import DiscordNotifier
from recommender import ClusteringRecommender


class OpenClawMonitor:
    DEFAULT_STATE_FILE = "seen_papers.json"

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.state_file = self.config.get("state_file", self.DEFAULT_STATE_FILE)
        self.seen_ids = self._load_seen_ids()
        self.arxiv = ArxivClient()
        self.notifier = DiscordNotifier(self.config.get("discord_webhook", ""), self.config.get("discord_username", "OpenClawBot"))
        self.recommender = ClusteringRecommender(self.config.get("k_clusters", 4))

    def _load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _load_seen_ids(self) -> set:
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as handle:
                return set(json.load(handle))
        return set()

    def _save_seen_ids(self) -> None:
        with open(self.state_file, "w", encoding="utf-8") as handle:
            json.dump(sorted(self.seen_ids), handle, indent=2)

    def _build_query(self) -> str:
        query_terms = self.config.get("arxiv_query", "all:machine learning")
        categories = self.config.get("categories", [])
        if categories:
            category_query = "+OR+".join([f"cat:{category}" for category in categories])
            return f"({query_terms})+AND+({category_query})"
        return query_terms

    def _get_interest_text(self) -> str:
        interests = self.config.get("interest_keywords", [])
        return " ".join(interests) if interests else self.config.get("arxiv_query", "")

    def _filter_new_papers(self, papers: List[Paper]) -> List[Paper]:
        return [paper for paper in papers if paper.id not in self.seen_ids]

    def _mark_seen(self, papers: List[Paper]) -> None:
        for paper in papers:
            self.seen_ids.add(paper.id)
        self._save_seen_ids()

    def run_once(self) -> None:
        query = self._build_query()
        max_results = int(self.config.get("max_results", 20))
        logging.info("Searching arXiv with query: %s", query)

        papers = self.arxiv.search(query, max_results=max_results)
        new_papers = self._filter_new_papers(papers)
        logging.info("Found %d total papers, %d new papers.", len(papers), len(new_papers))

        if not new_papers:
            logging.info("No new papers found.")
            return

        interest_text = self._get_interest_text()
        self.recommender.fit(new_papers)
        recommended = self.recommender.recommend(new_papers, interest_text, top_n=int(self.config.get("recommendation_count", 3)))

        if recommended:
            self.notifier.send_message(
                f"📢 New recommended research papers matching your interest: {interest_text}"
            )
            self.notifier.send_papers(recommended, "🔍 Recommended Paper")
        else:
            self.notifier.send_message(
                "📢 New papers were found, but none matched your saved interest keywords strongly enough."
            )

        self._mark_seen(new_papers)

    def run(self) -> None:
        interval_minutes = int(self.config.get("poll_interval_minutes", 30))
        while True:
            try:
                self.run_once()
            except Exception as exc:
                logging.exception("OpenClaw monitor failed: %s", exc)
            logging.info("Sleeping for %s minutes.", interval_minutes)
            time.sleep(interval_minutes * 60)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    monitor = OpenClawMonitor(config_path="config.yaml")
    monitor.run()


if __name__ == "__main__":
    main()
