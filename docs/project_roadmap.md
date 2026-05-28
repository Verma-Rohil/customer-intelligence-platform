# Project Roadmap & Sprint Planning Document
## Customer Intelligence & Retention Platform

| Field | Value |
| :--- | :--- |
| **Document Owner** | Rohil Verma |
| **Version** | 1.0 |
| **Created** | 2026-05-27 |
| **Status** | Approved for Development |
| **Timeline** | 7 Sprints (1 Week per Sprint, part-time) |

---

## Table of Contents
1. [Overview & Milestones](#1-overview--milestones)
2. [Sprint 1: Data Engineering & SQL Layer](#sprint-1-data-engineering--sql-layer)
3. [Sprint 2: EDA & Feature Engineering](#sprint-2-eda--feature-engineering)
4. [Sprint 3: Segmentation - Phase A (RFM & K-Means)](#sprint-3-segmentation---phase-a-rfm-&-k-means)
5. [Sprint 4: Segmentation - Phase B (Autoencoder + HDBSCAN)](#sprint-4-segmentation---phase-b-autoencoder--hdbscan)
6. [Sprint 5: Churn Classification & Explainability](#sprint-5-churn-classification--explainability)
7. [Sprint 6: Business Engine, API & Integration](#sprint-6-business-engine-api--integration)
8. [Sprint 7: React SPA Dashboard, Deployment & CI/CD](#sprint-7-react-spa-dashboard-deployment--cicd)

---

# 1. Overview & Milestones

This document provides a 7-week, sprint-by-sprint development roadmap designed to accommodate part-time work alongside M.Tech coursework. 

```
                                  PROJECT TIMELINE
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [Sprint 1] SQL Schema, Ingestion & Cohort Analytics Querying                   |
|       │                                                                         |
|       ▼                                                                         |
|  [Sprint 2] Exploratory Data Analysis & Feature Engineering Pipeline            |
|       │                                                                         |
|       ▼                                                                         |
|  [Sprint 3] Rule-Based RFM Scoring & Baseline K-Means Clustering                |
|       │                                                                         |
|       ▼                                                                         |
|  [Sprint 4] PyTorch Autoencoder & HDBSCAN Latent Clustering                     |
|       │                                                                         |
|       ▼                                                                         |
|  [Sprint 5] XGBoost Churn Prediction, SMOTE Balancing & SHAP Engine             |
|       │                                                                         |
|       ▼                                                                         |
|  [Sprint 6] FastAPI Backend Service & Campaign Simulation Engine                |
|       │                                                                         |
|       ▼                                                                         |
|  [Sprint 7] Multi-page React SPA UI, Docker Compose & GitHub Actions            |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### High-Level Milestones
- **Milestone 1 (End of Sprint 1)**: Database schema established, ETL running, and all 6 analytical SQL queries validated.
- **Milestone 2 (End of Sprint 2)**: Feature matrix generated containing 30+ validated features for all customer profiles.
- **Milestone 3 (End of Sprint 4)**: Multi-layer segmentation engine complete (RFM scores + baseline K-Means vs. Autoencoder + HDBSCAN embeddings).
- **Milestone 4 (End of Sprint 5)**: XGBoost classifier trained, tuned with Optuna, tracked in MLflow, and integrated with SHAP.
- **Milestone 5 (End of Sprint 6)**: FastAPI backend service running with Pydantic validations and passing unit tests.
- **Milestone 6 (End of Sprint 7)**: Complete system orchestrated via Docker Compose, passing CI/CD checks, and fully documented in the README.

---

# Sprint 1: Data Engineering & SQL Layer
*   **Goal**: Design the star schema, configure database indexes, and write initial analytical queries.
*   **Deliverables**: MySQL DDL scripts, Python ingestion scripts, and 6 core SQL analytical query scripts.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Set up the project directory structure, initialize the git repository, and download the raw e-commerce dataset. | `README.md`, `data/raw/` |
| **Day 2** | Write the DDL schema creation script containing table definitions, data types, constraints, and index optimizations. | `sql/01_schema_creation.sql` |
| **Day 3** | Write the Python ETL script to clean and cast raw CSV data, programmatically populate `dim_dates`, and load all tables. | `src/data_processing.py`, `sql/02_data_loading.sql` |
| **Day 4** | Write the RFM scoring SQL query utilizing `NTILE` window functions and CTEs. | `sql/03_rfm_analysis.sql` |
| **Day 5** | Write the monthly cohort retention query and advanced window analytics queries (running totals, lag differences). | `sql/04_cohort_analysis.sql`, `sql/05_churn_segmentation.sql`, `sql/06_advanced_analytics.sql` |

---

# Sprint 2: EDA & Feature Engineering
*   **Goal**: Profile the raw dataset, perform statistical testing, and write the feature engineering pipeline.
*   **Deliverables**: EDA Jupyter notebook, 15+ saved static plots, and the automated feature extraction module.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Profile feature distributions, identify skew, evaluate target class imbalance, and generate correlation heatmaps. | `notebooks/01_eda.ipynb` |
| **Day 2** | Perform statistical significance tests (Chi-square for categoricals, Welch's t-test for numericals) to identify churn drivers. | `notebooks/01_eda.ipynb` |
| **Day 3** | Save 15+ publication-quality plots (distributions, boxplots, heatmaps) to the plots folder. | `plots/eda/` |
| **Day 4** | Implement the feature extraction pipeline in Python to calculate the 30+ RFM, behavioral, and time-trend features. | `src/feature_engineering.py` |
| **Day 5** | Write feature imputation, encoding, and scaling pipelines (`RobustScaler` for skewed columns, `StandardScaler` for normal columns). | `notebooks/02_feature_engineering.ipynb` |

---

# Sprint 3: Segmentation - Phase A (RFM & K-Means)
*   **Goal**: Implement the rule-based RFM segmenter and the baseline K-Means clustering model.
*   **Deliverables**: RFM segmenter module, K-Means clustering model, and elbow/silhouette plots.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Implement the quartile RFM scoring and dictionary segment mapper in Python. | `src/rfm_segmentation.py` |
| **Day 2** | Build the K-Means pipeline: evaluate optimal clusters ($K$) using the Elbow method and Silhouette analysis. | `src/clustering/kmeans_baseline.py` |
| **Day 3** | Profile and document the resulting K-Means clusters (calculate mean feature values per cluster). | `notebooks/03_clustering.ipynb` |
| **Day 4** | Project the high-dimensional feature space to a 2D canvas using t-SNE / UMAP, and save the cluster visualization plot. | `plots/clustering/` |
| **Day 5** | Serialize the scaler and the trained K-Means model to the models folder. | `models/scaler.joblib`, `models/kmeans_model.joblib` |

---

# Sprint 4: Segmentation - Phase B (Autoencoder + HDBSCAN)
*   **Goal**: Implement the PyTorch Autoencoder representation pipeline and density clustering with HDBSCAN.
*   **Deliverables**: PyTorch Autoencoder script, saved weights, HDBSCAN cluster labels, and UMAP comparison plots.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Define the undercomplete Autoencoder class in PyTorch (layers: Input $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 16 $\rightarrow$ 32 $\rightarrow$ 64 $\rightarrow$ Output). | `src/clustering/autoencoder.py` |
| **Day 2** | Write the training loop, configure Adam optimization and MSE loss, set up early stopping, and save model weights. | `models/autoencoder_weights.pt` |
| **Day 3** | Extract the 16-dimensional bottleneck embeddings and run HDBSCAN density clustering. | `src/clustering/hdbscan_embeddings.py` |
| **Day 4** | Generate side-by-side UMAP comparisons of K-Means vs. Autoencoder + HDBSCAN. | `plots/clustering/comparison.png` |
| **Day 5** | Evaluate clustering performance (Silhouette score, Davies-Bouldin index) and document the results. | `notebooks/03_clustering.ipynb` |

---

# Sprint 5: Churn Classification & Explainability
*   **Goal**: Train baseline classifiers, tune the primary XGBoost model, and integrate SHAP explainability.
*   **Deliverables**: MLflow experiment logs, tuned XGBoost model binary, and SHAP explainer objects.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Train Logistic Regression and Random Forest baseline models using 5-Fold Stratified Cross-Validation. | `notebooks/04_churn_modeling.ipynb` |
| **Day 2** | Set up XGBoost training with SMOTE balancing, and integrate MLflow to track parameters and metrics. | `src/churn_model.py` |
| **Day 3** | Write the Optuna hyperparameter optimization script (50 trials) to optimize ROC-AUC. | `src/churn_model.py` |
| **Day 4** | Evaluate model performance (ROC curves, PR curves, Confusion Matrix) and serialize the best model. | `models/xgboost_churn_v1.joblib` |
| **Day 5** | Initialize the SHAP TreeExplainer, configure the background dataset, and save global summary and local waterfall plots. | `src/shap_explainer.py`, `plots/shap/` |

---

# Sprint 6: Business Engine, API & Integration
*   **Goal**: Build the campaign simulator, implement FastAPI routes, and write unit tests.
*   **Deliverables**: Business engine modules, FastAPI routing script, Pydantic schemas, and unit test suites.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Implement the Business Action Engine and the Campaign Simulator (ROI estimation formulas). | `src/retention_engine.py`, `src/campaign_simulator.py` |
| **Day 2** | Compute segment migrations over time using sequential batch snapshots. | `src/feature_engineering.py` |
| **Day 3** | Set up the FastAPI entry point, define Pydantic validation schemas, and construct request/response models. | `api/schemas.py`, `api/main.py` |
| **Day 4** | Implement the 5 core API endpoints (`/health`, `/model-info`, `/segment`, `/predict-churn`, `/simulate-campaign`). | `api/main.py` |
| **Day 5** | Write unit tests using pytest (feature engineering validations, model inference checks, API responses). | `tests/` |

---

# Sprint 7: React SPA Dashboard, Deployment & CI/CD
*   **Goal**: Build the modern Single Page Application in React, containerize services, and set up CI/CD.
*   **Deliverables**: React SPA frontend files, Dockerfiles, docker-compose configuration, and GitHub Actions workflows.

| Day | Task Detail | Associated Files |
| :--- | :--- | :--- |
| **Day 1** | Scaffold Vite + React app, build Executive Overview page and Model Performance page. | `frontend/package.json`, `frontend/src/pages/` |
| **Day 2** | Build the Customer Lookup page (with SHAP plots), Segment Deep Dive, and Campaign Simulator pages. | `frontend/src/pages/` |
| **Day 3** | Build the Segment Migration page (with Sankey diagrams) and global layout/sidebar. | `frontend/src/pages/`, `frontend/src/components/` |
| **Day 4** | Write the service Dockerfiles and `docker-compose.yml` to orchestrate both the FastAPI and React containers. | `api/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` |
| **Day 5** | Write the GitHub Actions workflow for testing and linting, and compile the final project README with architecture diagrams and screenshots. | `.github/workflows/ci.yml`, `README.md` |

---

> [!NOTE]
> Sprints are scoped to be independent and linear. To prevent bottleneck issues, ensure that all DDL scripts and analytical queries are completed and validated during Sprint 1 before starting the Python feature engine in Sprint 2.
