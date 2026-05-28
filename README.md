# Customer Intelligence & Retention Platform

An end-to-end machine learning system that transforms raw e-commerce transaction data into actionable customer segments, churn predictions, and campaign simulations — served through a FastAPI backend and visualized in a React dashboard.

Built on the [Brazilian E-Commerce (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) public dataset with ~100 k orders across 96 k unique customers.

---

## What This Project Does

1. **Ingests and cleans** seven raw CSV files, engineers 30+ behavioral features (RFM scores, purchase velocity, review sentiment, category diversity).
2. **Segments customers** using K-Means clustering on RFM dimensions, producing four distinct groups (Champions, Loyal, At-Risk, Hibernating).
3. **Predicts churn** with an XGBoost classifier (ROC-AUC 0.92, F1 0.82) trained on a 60-day inactivity target, with SHAP-based explainability for every prediction.
4. **Learns latent representations** through a PyTorch autoencoder for anomaly scoring and dimensionality reduction.
5. **Exposes inference endpoints** via a FastAPI service — segment a customer, predict churn probability, simulate campaign ROI.
6. **Visualizes everything** in an interactive React + shadcn/ui dashboard with executive KPIs, segment deep-dives, migration flows, and a campaign simulator.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data & ML | Python, pandas, scikit-learn, XGBoost, PyTorch, SHAP, Optuna |
| API | FastAPI, Pydantic, Uvicorn |
| Frontend | React 19, Vite, shadcn/ui, Tailwind CSS v4, Plotly.js, Framer Motion |
| Database | MySQL (schema + analytical SQL), SQLite (feature store) |
| Testing | pytest, ESLint |

---

## Project Structure

```
.
├── api/                  # FastAPI application (main, schemas, services)
├── src/                  # ML pipeline source code
│   ├── config.py         #   paths, DB credentials, constants
│   ├── data_processing.py#   raw data cleaning and merging
│   ├── feature_engineering.py # 30+ feature derivations
│   ├── train.py          #   model training orchestrator
│   ├── clustering/       #   K-Means, RFM scoring
│   └── models/           #   XGBoost, autoencoder, label generation
├── frontend/             # React + shadcn/ui dashboard
│   └── src/
│       ├── components/   #   reusable UI components (Cards, Layout)
│       └── pages/        #   7 dashboard views
├── notebooks/            # Jupyter EDA and experimentation
├── sql/                  # MySQL schema, RFM, cohort, churn queries
├── tests/                # pytest unit tests
├── plots/                # saved visualizations (EDA, clustering, SHAP)
├── docs/                 # design documents, wireframes, PRD
├── requirements.txt      # Python dependencies
└── .env.example          # environment variable template
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm (or pnpm)
- MySQL 8.0+ (optional — the app falls back to a local SQLite feature store)

### 1. Clone and set up the environment

```bash
git clone https://github.com/<YOUR_USERNAME>/customer-intelligence-platform.git
cd customer-intelligence-platform

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your MySQL credentials (or leave defaults for SQLite fallback)
```

### 3. Download the dataset

```bash
python src/download_olist.py
```

This pulls the Olist dataset from Kaggle into `data/raw/`.

### 4. Run the ML pipeline

```bash
python src/train.py
```

Produces trained models in `models/` and processed features in `data/processed/`.

### 5. Start the API server

```bash
uvicorn api.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/model-info` | Model metadata and performance metrics |
| POST | `/segment` | Classify a customer into a segment |
| POST | `/predict-churn` | Return churn probability and risk tier |
| POST | `/simulate-campaign` | Estimate ROI for a campaign targeting a segment |
| GET | `/api/executive-summary` | Aggregated KPIs for the dashboard |
| GET | `/api/feature-importance` | XGBoost global feature importances |
| GET | `/api/segment-data` | Sampled customer data for visualizations |

---

## Dashboard Pages

- **Home** — landing page with platform overview and quick-access cards
- **Executive Overview** — top-line KPIs, segment distributions, churn rate trends
- **Customer Lookup** — search by customer ID, view individual predictions and feature breakdown
- **Segment Deep Dive** — interactive scatter plots, segment profiles, PCA projections
- **Segment Migration** — Sankey-style flow showing how customers move between segments over time
- **Campaign Simulator** — model campaign ROI by segment, channel, and budget
- **Model Performance** — confusion matrix, ROC curve, precision-recall, SHAP feature importance

---

## ML Pipeline Details

### Feature Engineering (30+ features)

- **RFM**: recency, frequency, monetary value
- **Temporal**: purchase velocity, inter-purchase intervals, day-of-week patterns
- **Product**: category diversity, average item price, basket size
- **Review**: average rating, review count, sentiment indicators
- **Payment**: installment usage, payment method diversity

### Models

- **K-Means** (k=4) on standardized RFM features for customer segmentation
- **XGBoost Classifier** for churn prediction (hyperparameters tuned with Optuna)
- **PyTorch Autoencoder** for learned embeddings and anomaly detection

### Explainability

SHAP values computed for every prediction, surfaced in the dashboard and available through the API for full model transparency.

---

## Tests

```bash
pytest tests/ -v
```

---

## License

This project is for portfolio and educational purposes. The underlying Olist dataset is publicly available on Kaggle under its original license.

---

## Contact

Built by **Rohil** — feel free to reach out for questions or collaboration.
