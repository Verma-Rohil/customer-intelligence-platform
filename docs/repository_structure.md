# Repository Structure Plan
## Customer Intelligence & Retention Platform

| Field | Value |
| :--- | :--- |
| **Document Owner** | Rohil Verma |
| **Version** | 1.0 |
| **Created** | 2026-05-27 |
| **Status** | Approved for Development |

---

## Table of Contents
1. [Directory Tree Specification](#1-directory-tree-specification)
2. [Folder & File Descriptions](#2-folder-&-file-descriptions)
3. [Git Branching & Workflow Strategy](#3-git-branching-&-workflow-strategy)
4. [Coding Standards & Linting Policies](#4-coding-standards-&-linting-policies)
5. [CI/CD Pipeline Integration](#5-cicd-pipeline-integration)

---

# 1. Directory Tree Specification

The project structure is organized to separate model training pipelines, the FastAPI serving layer, and the Streamlit visualization interface.

```
customer-intelligence-platform/
│
├── .github/                           # CI/CD Workflows
│   └── workflows/
│       └── ci.yml                     # Runs pytest and ruff linting
│
├── data/                              # Data Storage (gitignored if large)
│   ├── raw/                           # Original Kaggle CSV source files
│   └── processed/                     # Cleaned features and engineered tensors
│
├── sql/                               # SQL Analytics Layer
│   ├── 01_schema_creation.sql         # DDL schemas and database constraints
│   ├── 02_data_loading.sql            # Script for data ingestion
│   ├── 03_rfm_analysis.sql            # RFM quartile segment calculations
│   ├── 04_cohort_analysis.sql         # Monthly cohort retention matrices
│   ├── 05_churn_segmentation.sql      # Multi-table join aggregations
│   └── 06_advanced_analytics.sql      # LAG/LEAD and running total metrics
│
├── notebooks/                         # Exploratory Research
│   ├── 01_eda.ipynb                   # Distribution plots & statistical testing
│   ├── 02_feature_engineering.ipynb   # Feature prototyping and documentation
│   ├── 03_clustering.ipynb            # K-Means baseline vs Autoencoder + HDBSCAN
│   └── 04_churn_modeling.ipynb        # Churn modeling, hyperparameter tuning & SHAP
│
├── src/                               # Package Core source code
│   ├── __init__.py
│   ├── config.py                      # Global parameters, paths, seeds
│   ├── data_processing.py             # Python ETL database connectors
│   ├── feature_engineering.py         # 30+ feature computation pipelines
│   ├── rfm_segmentation.py            # Layer 1: RFM scoring execution
│   ├── clustering/                    # Layer 2: Clustering pipelines
│   │   ├── __init__.py
│   │   ├── kmeans_baseline.py         # K-Means model training
│   │   ├── autoencoder.py             # PyTorch network specifications
│   │   └── hdbscan_embeddings.py      # HDBSCAN clustering on embeddings
│   ├── churn_model.py                 # Layer 3: XGBoost training pipelines
│   ├── shap_explainer.py              # SHAP model explainers
│   ├── retention_engine.py            # Business Action mappings
│   └── campaign_simulator.py          # ROI estimation calculations
│
├── api/                               # FastAPI Serving Microservice
│   ├── Dockerfile                     # API container build instructions
│   ├── main.py                        # FastAPI endpoints and startup events
│   ├── schemas.py                     # Pydantic request/response models
│   └── requirements.txt              # FastAPI specific dependencies
│
├── frontend/                          # Visualization & Frontend Layer (React + Vite)
│   ├── package.json                   # NPM dependencies
│   ├── vite.config.js                 # Vite bundler configuration
│   └── src/
│       ├── main.jsx                   # React application entry point
│       ├── App.jsx                    # Root router and global layout
│       ├── App.css                    # Global design system CSS
│       ├── api/
│       │   └── client.js              # Centralized HTTP fetch wrapper for FastAPI
│       ├── components/                # Reusable UI components
│       ├── pages/                     # React Router page views
│       └── styles/                    # CSS Custom Properties (Tokens)
│
├── models/                            # Model Checkpoints (gitignored except placeholder)
│   ├── .gitkeep
│   ├── xgboost_churn_v1.joblib        # Serialized churn model
│   ├── autoencoder_weights.pt         # Serialized PyTorch weights
│   ├── scaler.joblib                  # Robust/Standard preprocessor scaler
│   ├── encoders.joblib                # Categorical encoder mappings
│   └── kmeans_model.joblib            # Serialized K-Means baseline
│
├── plots/                             # Saved Static Visualizations
│   ├── .gitkeep
│   ├── eda/                           # Sprint 2 profiling plots
│   ├── clustering/                    # Sprint 3/4 UMAP scatter plots
│   ├── shap/                          # Sprint 5 beeswarm & waterfall plots
│   └── campaign/                      # Sprint 6 campaign ROI plots
│
├── tests/                             # Unit Test Suite
│   ├── test_feature_engineering.py
│   ├── test_churn_model.py
│   ├── test_api.py
│   ├── test_campaign_simulator.py
│   └── test_autoencoder.py
│
├── docker-compose.yml                 # Service Orchestration file
├── .env.example                       # Environment template variables
├── .gitignore                         # Python, OS, Jupyter, and MLflow ignores
└── requirements.txt                   # Global project requirements
```

---

# 2. Folder & File Descriptions

### 2.1 Configuration & Core Packages (`src/`)
*   `src/config.py`: Central config module storing seeds, input data dimensions, database connection credentials loaded from `.env`, file paths, and default model hyperparameter settings.
*   `src/data_processing.py`: Handles raw CSV ingestion, data parsing, and SQL database loading, serving as our ETL pipeline.
*   `src/feature_engineering.py`: Processes query outputs and transforms them into standard numerical features (scaling, imputation, categorical encoding).

### 2.2 Serving Layer (`api/`)
*   `api/main.py`: Exposes model inference routes, handles Pydantic validation schemas, and processes SHAP explanations.
*   `api/schemas.py`: Defines request/response Pydantic models to ensure type safety.

### 2.3 Visualization Layer (`frontend/`)
The `frontend/` directory contains a modern Single Page Application (SPA) built with React 19 and Vite. It serves as the interactive business interface for the intelligence platform.
- `src/pages/`: Contains the React Router views mapping to the various analytical dashboards (e.g., Executive Overview, Customer Lookup).
- `src/components/`: Reusable modular UI elements, including glassmorphism cards and a Plotly.js chart wrapper for 3D PCA, Sankey flows, and SHAP visualizations.
- `src/api/client.js`: A centralized fetch client that communicates with the local FastAPI endpoints.

---

# 3. Git Branching & Workflow Strategy

To maintain a clean codebase during development, we use a structured Git branching strategy.

```
                      +-----------------------------+
                      |         main (Prod)         |
                      +-----------------------------+
                                     |
                                     v  Merge Releases
                      +-----------------------------+
                      |         develop (Dev)       |
                      +-----------------------------+
                                     |
         +---------------------------+---------------------------+
         v                                                       v
+-----------------------+                               +-----------------------+
|  feature/sql-layer    |                               |  feature/ml-modeling  |
+-----------------------+                               +-----------------------+
```

### Branch Classifications
*   **`main`**: Production-ready code. Commits are restricted to merges from the release branches.
*   **`develop`**: The primary development branch. Sprints merge code here for testing before release.
*   **`feature/*`**: Short-lived branches created for specific sprint tasks (e.g., `feature/sql-layer`, `feature/autoencoder-model`).

---

# 4. Coding Standards & Linting Policies

To comply with PEP 8 coding standards, we use **Ruff** for linting and formatting.

### Core Policies
1.  **Type Hints**: All public function signatures must include type annotations:
    ```python
    def calculate_roi(segment_size: int, avg_clv: float, cost: float) -> float:
        ...
    ```
2.  **Docstrings**: All modules, classes, and public functions must document inputs, outputs, and behaviors using Google Style docstrings.
3.  **Reproducibility**: Set a global random seed (`42`) across all random generation engines (NumPy, Scikit-learn, PyTorch, XGBoost).

---

# 5. CI/CD Pipeline Integration

A GitHub Actions workflow (.github/workflows/ci.yml) executes on every push or pull request to `develop` and `main` to run tests and verify code formatting.

```
                  [Code Push / Pull Request]
                              |
                              v  Triggers GitHub Actions
                       +--------------+
                       | CI/CD Runner |
                       +--------------+
                              |
               +--------------+--------------+
               v                             v
       +---------------+             +---------------+
       |  Ruff Lint    |             |  Pytest Suite |
       |  - Style check|             |  - Run unit   |
       |  - Format check|            |    tests      |
       +---------------+             +---------------+
```

### Workflow Configuration
- **Runner**: `ubuntu-latest`.
- **Environment**: Python 3.11.
- **Verification Steps**:
  1.  Checkout code.
  2.  Install pinned dependencies: `pip install -r requirements.txt`.
  3.  Run style check: `ruff check .`.
  4.  Execute unit tests: `pytest tests/`.

---

> [!WARNING]
> Do not commit large CSV datasets or local MLflow logs (`mlruns/`) to the remote repository. Ensure that the `.gitignore` file includes patterns for `/data/raw/`, `mlruns/`, `mlflow.db`, and `venv/`.
