
import json
import random
import re
from difflib import SequenceMatcher


THRESHOLD = 0.45

NORMALISASI = {
    "gmn": "bagaimana",
    "gimana": "bagaimana",
    "gmna": "bagaimana",
    "brp": "berapa",
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "tdk": "tidak",
    "udah": "sudah",
    "udh": "sudah",
    "utk": "untuk",
    "dgn": "dengan",
    "yg": "yang",
    "bs": "bisa",
    "makasi": "makasih"
}

STOPWORDS = {
    "yang", "di", "ke", "dari", "itu", "ini", "dong",
    "deh", "ya", "sih", "aku", "saya", "kamu", "apa",
    "aja", "nih", "tuh", "dan", "atau", "untuk",
    "dengan", "kalau"
}


def load_theme(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def preprocess(text):
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())

    tokens = []

    for word in text.split():
        word = NORMALISASI.get(word, word)

        for token in word.split():
            if token and token not in STOPWORDS:
                tokens.append(token)

    return tokens


def similarity(a, b):
    if not a or not b:
        return 0.0

    set_a = set(a)
    set_b = set(b)

    same = len(set_a & set_b)

    jaccard = same / len(set_a | set_b)

    fuzzy = SequenceMatcher(
        None,
        " ".join(a),
        " ".join(b)
    ).ratio()

    coverage = same / len(set_b)

    return (
        0.4 * jaccard +
        0.3 * fuzzy +
        0.3 * coverage
    )


class ChatbotEngine:

    def __init__(self, theme, threshold=THRESHOLD):
        self.theme = theme
        self.threshold = threshold

        self.patterns = []
        self.responses = {}

        for intent in theme["intents"]:
            tag = intent["tag"]

            self.responses[tag] = intent["responses"]

            for pattern in intent["patterns"]:
                self.patterns.append((
                    tag,
                    preprocess(pattern)
                ))

    def classify(self, message):
        tokens = preprocess(message)

        best_score = 0
        best_tag = None

        for tag, pattern_tokens in self.patterns:
            score = similarity(tokens, pattern_tokens)

            if score > best_score:
                best_score = score
                best_tag = tag

        if best_score >= self.threshold:
            return best_tag, round(best_score, 2)

        return None, round(best_score, 2)

    def reply(self, message):
        tag, score = self.classify(message)

        if tag is None:
            answers = self.theme["fallback"]
        else:
            answers = self.responses[tag]

        return {
            "reply": random.choice(answers),
            "intent": tag,
            "score": score
        }