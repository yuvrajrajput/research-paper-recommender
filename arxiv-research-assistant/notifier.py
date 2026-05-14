import logging
from typing import List

import requests

from models import Paper


class DiscordNotifier:
    def __init__(self, webhook_url: str, username: str = "OpenClawBot"):
        self.webhook_url = webhook_url
        self.username = username

    def send_message(self, content: str) -> None:
        if not self.webhook_url:
            logging.warning("Discord webhook URL is not configured.")
            return

        payload = {
            "username": self.username,
            "content": content,
        }
        response = requests.post(self.webhook_url, json=payload, timeout=15)
        response.raise_for_status()

    def send_papers(self, papers: List[Paper], header: str) -> None:
        if not papers:
            return

        for paper in papers:
            lines = [
                f"**{paper.title}**",
                f"Authors: {', '.join(paper.authors)}",
                f"Categories: {', '.join(paper.categories)}",
                f"Published: {paper.published}",
                f"Score: {paper.score:.4f}",
                f"Link: {paper.link}",
            ]
            body = "\n".join(lines)
            self.send_message(f"{header}\n{body}")
