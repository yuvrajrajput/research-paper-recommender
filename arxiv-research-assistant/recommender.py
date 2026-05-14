from typing import List, Optional

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models import Paper


class ClusteringRecommender:
    def __init__(self, k_clusters: int, stop_words: str = "english"):
        self.k_clusters = max(1, k_clusters)
        self.vectorizer = TfidfVectorizer(max_df=0.85, min_df=1, stop_words=stop_words, ngram_range=(1, 2))
        self.kmeans: Optional[KMeans] = None
        self.embeddings = None

    def fit(self, papers: List[Paper]) -> None:
        corpus = [f"{paper.title}. {paper.summary}" for paper in papers]
        self.embeddings = self.vectorizer.fit_transform(corpus)
        cluster_count = min(self.k_clusters, len(papers))
        self.kmeans = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
        self.kmeans.fit(self.embeddings)
        labels = self.kmeans.labels_.tolist()
        for paper, label in zip(papers, labels):
            paper.cluster = int(label)

    def recommend(self, papers: List[Paper], interest_text: str, top_n: int = 5) -> List[Paper]:
        if not papers or self.embeddings is None:
            return []

        interest_vec = self.vectorizer.transform([interest_text])
        similarities = cosine_similarity(self.embeddings, interest_vec).flatten()
        for paper, score in zip(papers, similarities):
            paper.score = float(score)

        if self.kmeans is not None:
            centroid_scores = cosine_similarity(self.kmeans.cluster_centers_, interest_vec).flatten()
            best_clusters = centroid_scores.argsort()[::-1][:2]
            clustered = [paper for paper in papers if paper.cluster in best_clusters]
            clustered.sort(key=lambda p: p.score, reverse=True)
            if clustered:
                return clustered[:top_n]

        return sorted(papers, key=lambda p: p.score, reverse=True)[:top_n]
