from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
from typing import List, Dict

analyzer = SentimentIntensityAnalyzer()

def sentiment_from_headlines(headlines: List[str]) -> Dict[str, float]:
    if not headlines:
        return {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 0.0}
    scores = [analyzer.polarity_scores(h) for h in headlines]
    df = pd.DataFrame(scores)
    return df.mean().to_dict()

def cluster_headlines(headlines: List[str], n_clusters: int = 3) -> Dict[int, List[str]]:
    if len(headlines) < 2:
        return {0: headlines}
    vec = TfidfVectorizer(stop_words='english', max_features=500)
    X = vec.fit_transform(headlines)
    k = min(n_clusters, len(headlines))
    km = KMeans(n_clusters=k, random_state=0, n_init=10).fit(X)  # Explicit n_init to avoid warning
    clusters = {}
    for i, label in enumerate(km.labels_):
        clusters.setdefault(label, []).append(headlines[i])
    return clusters