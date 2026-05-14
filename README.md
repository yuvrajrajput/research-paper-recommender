# OpenClaw Research Monitor

OpenClaw is a Python monitor for new arXiv research papers. It polls the arXiv API, filters for new papers, clusters them using k-means, ranks papers against your interest keywords, and sends recommendations to a Discord webhook.

## What it does

- Fetches new papers from arXiv using the official API.
- Stores seen paper IDs so notifications only fire for new research.
- Uses TF-IDF and k-means clustering to organize similar papers.
- Recommends only the most relevant papers to your interests.
- Sends notifications to Discord using a webhook.

## Setup

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Update `config.yaml`:

- `discord_webhook`: your Discord webhook URL
- `arxiv_query`: arXiv search query
- `categories`: arXiv categories to filter
- `interest_keywords`: keywords describing your research interests
- `k_clusters`: how many clusters to create for recommendations
- `recommendation_count`: how many papers to recommend per run
- `poll_interval_minutes`: how often to check for new papers

3. Run the monitor:

```bash
python openclaw.py
```

## Notes

- The tool saves seen paper IDs in `seen_papers.json`.
- If you want to test quickly, set `poll_interval_minutes` to a smaller value.
- Use strong interest keywords to get more focused recommendations.
