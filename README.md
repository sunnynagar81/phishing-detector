# PhishGuard AI: Phishing Detection with a Chrome Extension

An AI-powered system that detects phishing in **URLs, emails and SMS messages**. A Chrome extension scans each page you visit through a FastAPI backend and shows a security verdict with the reasons behind it. A React dashboard shows scan history and analytics.

## Modules

| Module | What it does |
|---|---|
| URL Detection | Extracts 28 features from a URL and classifies it with a Random Forest |
| Email Detection | TF-IDF + Logistic Regression on subject and body, plus link checking |
| SMS Detection | TF-IDF + Logistic Regression, plus link checking |
| AI/ML Engine | Trained models, feature extraction, SHAP and word-level explanations |
| Chrome Extension | Manifest V3 extension: auto-scans each page, badge + popup |
| Dashboard | React app: stats, charts, manual scanning, history |

## Architecture

```
Chrome Extension ──(URL)──► FastAPI ──► ML Engine ──► SHAP / word explanation
        ▲                      │
        └──(verdict + reasons)─┤
                               ▼
                    MongoDB (scan history)
                               │
                               ▼
                       React Dashboard
```

## Tech stack

Python, FastAPI, scikit-learn, Pandas, NumPy, SHAP, MongoDB (PyMongo), React (Vite), Recharts, Chrome Manifest V3.

## Results

| Model | Dataset | Phishing precision | Phishing recall | F1 |
|---|---|---|---|---|
| URL (Random Forest) | Kaggle Phishing Site URLs + Tranco top-50k | 0.93 | 0.75 | 0.83 |
| SMS (TF-IDF + LR) | UCI SMS Spam Collection | 0.91 | 0.89 | 0.90 |
| Email (TF-IDF + LR) | CEAS-08 | 1.00 | 0.99 | 1.00 |

## Setup

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```
Create `backend/.env`:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=phishing_db
```

### 2. Datasets (not included in the repo)
Place in `backend/data/`:
- `phishing_site_urls.csv` (Kaggle: Phishing Site URLs)
- `emails.csv` (CEAS_08.csv from the Kaggle Phishing Email Dataset)
- `sms_spam.tsv` (UCI SMS Spam Collection)

### 3. Train the models
```bash
python app/ml/get_tranco.py
python app/ml/train_url.py
python app/ml/train_text.py
```

### 4. Run the API
```bash
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### 5. Chrome extension
1. Open `chrome://extensions` and enable Developer mode.
2. Click **Load unpacked** and select the `extension` folder.

###