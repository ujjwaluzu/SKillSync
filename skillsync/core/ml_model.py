import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack

# Load dataset
df = pd.read_csv("core/data/dataset.csv")

# -----------------------------
# 🔹 FEATURE ENGINEERING
# -----------------------------

def extract_extra_features(text):
    text = text.lower()

    return [
        text.count("with"),                 # number of features
        int("ecommerce" in text),
        int("ai" in text or "machine learning" in text),
        int("chat" in text),
        int("dashboard" in text),
        int("payment" in text),
        int("real-time" in text),
        int("advanced" in text),
        int("intermediate" in text),
        int("basic" in text),
    ]


extra_features = np.array([extract_extra_features(t) for t in df["description"]])

# -----------------------------
# 🔹 TEXT FEATURES (TF-IDF)
# -----------------------------

vectorizer = TfidfVectorizer(max_features=800)
X_text = vectorizer.fit_transform(df["description"])

# -----------------------------
# 🔹 COMBINE FEATURES
# -----------------------------

X = hstack([X_text, extra_features])

y = df["price"]

# -----------------------------
# 🔹 MODEL (UPGRADED)
# -----------------------------

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42
)

model.fit(X, y)

# -----------------------------
# 🔹 PREDICTION FUNCTION
# -----------------------------

def predict_price(text):
    text_vec = vectorizer.transform([text])
    extra = np.array([extract_extra_features(text)])

    combined = hstack([text_vec, extra])

    # Get predictions from all trees
    preds = [tree.predict(combined)[0] for tree in model.estimators_]

    avg = np.mean(preds)
    min_p = np.min(preds)
    max_p = np.max(preds)

    return int(min_p), int(max_p), int(avg)


def estimate_time(avg_price):
    if avg_price < 20000:
        return "3-7 days"
    elif avg_price < 50000:
        return "1-3 weeks"
    else:
        return "3-6 weeks"