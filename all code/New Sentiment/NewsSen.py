import feedparser
import hashlib
import os
import json
from datetime import datetime, timedelta

from newspaper import Article
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class NewsSentiment:
    def __init__(self, company='nvidia', max_articles=20, seen_file=None, days_back=5, ignore_seen=False):
        self.company = company.lower()
        self.max_articles = max_articles
        self.seen_file = seen_file
        self.days_back = days_back
        self.ignore_seen = ignore_seen

        self.rss_url = f'https://news.google.com/rss/search?q={company}&hl=en-US&gl=US&ceid=US:en'
        self.sentiment_scores = {
            'Strongly Negative': -2,
            'Negative': -1,
            'Neutral': 0,
            'Positive': 1,
            'Strongly Positive': 2
        }

        nltk.download('vader_lexicon', quiet=True)
        self.analyzer = SentimentIntensityAnalyzer()
        self.seen_hashes = self._load_seen_hashes()

        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    def _load_seen_hashes(self):
        if self.seen_file and os.path.exists(self.seen_file):
            with open(self.seen_file, 'r') as f:
                return set(json.load(f))
        return set()

    def _fetch_articles(self):
        feed = feedparser.parse(self.rss_url)
        new_entries = []
        cutoff = datetime.now() - timedelta(days=self.days_back)

        for entry in feed.entries:
            if len(new_entries) >= self.max_articles:
                break
            article_hash = hashlib.md5(entry.link.encode('utf-8')).hexdigest()
            pub_date = datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else datetime.now()
            if self.ignore_seen or (article_hash not in self.seen_hashes and pub_date >= cutoff):
                entry.published_dt = pub_date
                new_entries.append(entry)
                if not self.ignore_seen and self.seen_file:
                    self.seen_hashes.add(article_hash)
        return new_entries

    def _extract_text(self, url, title=""):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return f"{title}\n\n{article.text}", title
        except:
            return title, title

    def _finbert_sentiment(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        labels = ["Negative", "Neutral", "Positive"]
        return labels[probs.argmax().item()], float(probs.max())

    def _classify_sentiment(self, text, title=""):
        if not text.strip():
            return "Neutral"

        vader_score = self.analyzer.polarity_scores(text)['compound']
        title_score = self.analyzer.polarity_scores(title)['compound']
        combined_vader = 0.7 * vader_score + 0.3 * title_score

        finbert_sentiment, confidence = self._finbert_sentiment(text)

        if confidence > 0.8:
            return finbert_sentiment
        else:
            if combined_vader <= -0.7:
                return "Strongly Negative"
            elif combined_vader <= -0.2:
                return "Negative"
            elif combined_vader >= 0.7:
                return "Strongly Positive"
            elif combined_vader >= 0.2:
                return "Positive"
            else:
                return "Neutral"

    def analyze(self, verbose=True):
        articles = self._fetch_articles()
        total_score = 0
        count = 0
        sentiment_counts = {k: 0 for k in self.sentiment_scores}

        if verbose:
            print(f"\n📰 Found {len(articles)} recent articles:\n")

        for entry in articles:
            text, title = self._extract_text(entry.link, entry.title)
            sentiment = self._classify_sentiment(text, title)
            sentiment_counts[sentiment] += 1
            total_score += self.sentiment_scores[sentiment]
            count += 1

        avg = round(total_score / count) if count > 0 else 0

        if avg == 0:
            most_common = max(sentiment_counts.items(), key=lambda x: x[1])[0]
            if verbose:
                print(f"Tie detected. Breaking tie with most frequent sentiment: {most_common}")
            avg = self.sentiment_scores[most_common]

        return avg
