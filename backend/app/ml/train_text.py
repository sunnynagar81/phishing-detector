import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

sys.path.append(str(Path(__file__).resolve().parents[2]))

OUT_DIR = Path("app/models")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def train(name, texts, labels):
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, stratify=labels, random_state=42
    )
    pipe = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000,
                        sublinear_tf=True, stop_words="english"),
        LogisticRegression(max_iter=2000, class_weight="balanced"),
    )
    print(f"\n=== Training {name} model ===")
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    print(classification_report(y_test, pred, target_names=["safe", "phishing"]))
    print(confusion_matrix(y_test, pred))
    joblib.dump(pipe, OUT_DIR / f"{name}_model.joblib")
    print(f"Saved app/models/{name}_model.joblib")


# ---------- SMS ----------
sms = pd.read_csv("data/sms_spam.tsv", sep="\t", header=None, names=["label", "text"]).dropna()
sms = sms.drop_duplicates(subset="text")
train("sms", sms["text"], (sms["label"] == "spam").astype(int))

# ---------- Email ----------
em = pd.read_csv("data/emails.csv").dropna(subset=["body", "label"])
em["text"] = em["subject"].fillna("") + " " + em["body"].astype(str)
em = em.drop_duplicates(subset="text")
train("email", em["text"], em["label"].astype(int))