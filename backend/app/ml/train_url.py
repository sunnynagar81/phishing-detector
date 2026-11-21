import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.append(str(Path(__file__).resolve().parents[2]))
from app.ml.features import extract_features, FEATURE_NAMES

DATA = Path("data/phishing_site_urls.csv")
TRANCO = Path("data/tranco_top.csv")
OUT = Path("app/models/url_model.joblib")


def featurize(urls):
    return pd.DataFrame([extract_features(u) for u in urls])[FEATURE_NAMES]


print("Loading data...")
df = pd.read_csv(DATA).dropna().drop_duplicates(subset="URL")
df["target"] = (df["Label"].str.lower() == "bad").astype(int)  # 1 = phishing

# Legitimate popular domains (Tranco): train on ranks 1-50000, hold out 50001-55000
domains = [line.split(",")[1].strip() for line in TRANCO.read_text().splitlines() if "," in line]
train_domains, held_domains = domains[:50000], domains[50000:55000]


def tranco_urls(doms):
    return [f"https://{d}" for d in doms] + [f"https://www.{d}/" for d in doms]


tranco_df = pd.DataFrame({"URL": tranco_urls(train_domains)})
tranco_df["target"] = 0

train_df, test_df = train_test_split(
    df[["URL", "target"]], test_size=0.2, stratify=df["target"], random_state=42
)
train_df = pd.concat([train_df, tranco_df], ignore_index=True)
print(train_df["target"].value_counts())

print("Extracting features (a few minutes)...")
X_train, y_train = featurize(train_df["URL"]), train_df["target"]
X_test, y_test = featurize(test_df["URL"]), test_df["target"]
X_held = featurize(tranco_urls(held_domains))  # unseen real sites, all should be safe

models = {
    "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    # Smaller forest so the saved file fits on GitHub and Render's free tier
    "random_forest": RandomForestClassifier(
        n_estimators=80, max_depth=18, min_samples_leaf=10, n_jobs=-1, random_state=42
    ),
    "gradient_boosting": HistGradientBoostingClassifier(random_state=42),
}

best_name, best_model, best_f1 = None, None, 0
for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    f1 = f1_score(y_test, pred)
    held_safe = (model.predict(X_held) == 0).mean()
    print(classification_report(y_test, pred, target_names=["safe", "phishing"]))
    print(confusion_matrix(y_test, pred))
    print(f"Unseen popular sites predicted safe: {held_safe:.1%}")
    if f1 > best_f1:
        best_name, best_model, best_f1 = name, model, f1

print(f"\nBest model: {best_name} (F1 = {best_f1:.4f})")
OUT.parent.mkdir(parents=True, exist_ok=True)
joblib.dump({"model": best_model, "features": FEATURE_NAMES, "name": best_name}, OUT, compress=3)
print(f"Saved to {OUT}")