# Experiment Tracking Strategy Document
## Customer Intelligence & Retention Platform

| Field | Value |
| :--- | :--- |
| **Document Owner** | Rohil Verma |
| **Version** | 1.0 |
| **Created** | 2026-05-27 |
| **Status** | Approved for Development |
| **Tracking Framework**| MLflow 2.x |
| **Backend Store** | Local SQLite Database (`sqlite:///mlflow.db`) |
| **Artifact Store** | Local directory (`./mlruns/`) |

---

## Table of Contents
1. [MLflow Architecture & Configuration](#1-mlflow-architecture--configuration)
2. [Experiment Structure & Naming Conventions](#2-experiment-structure--naming-conventions)
3. [Logged Parameters & Hyperparameters](#3-logged-parameters--hyperparameters)
4. [Logged Metrics & Performance History](#4-logged-metrics--performance-history)
5. [Artifact Logging Specification](#5-artifact-logging-specification)
6. [Model Registry & Deployment Transitions](#6-model-registry--deployment-transitions)

---

# 1. MLflow Architecture & Configuration

To ensure model reproducibility, comparison, and auditability, all model training phases are tracked using **MLflow**.

```
    [Model Training Pipeline (XGBoost / PyTorch)]
                         |
                         v  Params, Metrics, Artifacts
    +----------------------------------------------------+
    |                    MLflow Client                   |
    +----------------------------------------------------+
              |                                 |
              v                                 v
    +-------------------+             +--------------------+
    |   Backend Store   |             |   Artifact Store   |
    |  - SQLite DB      |             |  - Local File Dir  |
    |  - Run metadata   |             |  - Model weights   |
    |  - Params/Metrics |             |  - Plots & logs    |
    +-------------------+             +--------------------+
```

### Logging Configuration
- **Backend Store**: SQLite database (`mlflow.db`) initialized locally to store run metadata, parameters, and metrics.
- **Artifact Store**: Local directory `./mlruns/` to save serialized model weights, feature scalers, encoders, and evaluation plots.
- **In-Memory Tracking**: During pipeline execution, MLflow metrics are updated dynamically using the active run context:
  ```python
  import mlflow
  mlflow.set_tracking_uri("sqlite:///mlflow.db")
  ```

---

# 2. Experiment Structure & Naming Conventions

Experiments are grouped into distinct projects matching our modeling phases.

```
MLflow Runs
 ├── Experiment: customer_segmentation_autoencoder ---> PyTorch weights, bottleneck loss
 └── Experiment: customer_churn_prediction ------------> XGBoost models, Optuna runs, SHAP plots
```

### Experiment Identifiers
1. **`customer_segmentation_autoencoder`**: Tracks autoencoder reconstruction performance, reconstruction MSE loss per epoch, bottleneck latent dimension sizes, and early stopping iterations.
2. **`customer_churn_prediction`**: Tracks churn classifiers, including baseline runs (Logistic Regression, Random Forest) and the hyperparameter tuning trials of our primary XGBoost model.

### Run Naming Conventions
Individual runs use structured naming tags:
`[Algorithm_Name]_[Imbalance_Method]_[Trial_Index]`
*   *Example 1*: `XGBoost_SMOTE_trial_04`
*   *Example 2*: `RandomForest_Baseline`

---

# 3. Logged Parameters & Hyperparameters

For every pipeline run, MLflow logs the following configuration settings:

### 3.1 Churn Prediction Models (XGBoost)
*   **Data Pipeline Configuration**:
    - `imbalance_strategy`: (`"SMOTE"`, `"scale_pos_weight"`, or `"None"`).
    - `scaling_method`: (`"StandardScaler"`, `"RobustScaler"`, or `"MinMaxScaler"`).
    - `test_split_ratio`: Hold-out test percentage (default: `0.20`).
    - `cv_folds`: Number of stratified validation folds (default: `5`).
*   **Model Hyperparameters**:
    - `n_estimators`, `max_depth`, `learning_rate`, `gamma`, `subsample`, `colsample_bytree`, `min_child_weight`.

### 3.2 Autoencoder Models (PyTorch)
*   **Network Architecture**:
    - `input_dim`: Count of raw input features.
    - `bottleneck_dim`: Dimension of latent representation layer (default: `16`).
    - `hidden_layers`: Network layout (default: `[64, 32]`).
*   **Training Parameters**:
    - `learning_rate`, `batch_size`, `epochs`, `weight_decay`, `early_stopping_patience`.

---

# 4. Logged Metrics & Performance History

Metrics are tracked across the training lifecycle to monitor validation curves and identify overfitting.

### 4.1 Churn Model Metrics
Logged at the end of each validation fold, with final averages evaluated on the hold-out test split:

| Metric Name | Logging Stage | Purpose |
| :--- | :--- | :--- |
| `roc_auc` | Fold End / Final Test | Primary model evaluation metric. |
| `f1_score` | Fold End / Final Test | Evaluates balance on imbalanced classes. |
| `recall` | Fold End / Final Test | Measures the proportion of actual churners identified. |
| `precision` | Fold End / Final Test | Measures the accuracy of positive churn predictions. |
| `training_loss` | Epoch End (XGBoost) | Monitored to detect early convergence. |

### 4.2 Autoencoder Metrics
- `train_mse_loss`: Reconstruction loss on the training split, logged at the end of each epoch.
- `val_mse_loss`: Reconstruction loss on the validation split, logged at the end of each epoch.

---

# 5. Artifact Logging Specification

Model assets are serialized and logged as run artifacts.

```
Logged Run Artifacts
 ├── models/
 │    ├── model.joblib                 # Serialized model binary
 │    ├── scaler.joblib                # Preprocessing scaler
 │    └── autoencoder_weights.pt       # PyTorch weights
 └── evaluation_plots/
      ├── confusion_matrix.png         # Heatmap plot
      ├── roc_curve.png                # ROC curve plot
      └── shap_summary.png             # SHAP beeswarm plot
```

### Serialized Weights & Preprocessors
*   `models/model.joblib`: The fitted XGBoost or Random Forest model.
*   `models/scaler.joblib`: The fitted robust/standard scaling pipeline.
*   `models/autoencoder_weights.pt`: PyTorch weights of the autoencoder.

### Evaluation Visualizations
*   `plots/confusion_matrix.png`: Heatmap plot of the classification confusion matrix.
*   `plots/roc_curve.png`: Evaluation plot showing the ROC and Precision-Recall curves.
*   `plots/shap_summary.png`: SHAP beeswarm plot displaying global feature impact.

---

# 6. Model Registry & Deployment Transitions

The MLflow Model Registry manages model versioning and promotion to production.

```
              [Optuna Optimization Loop]
                          |
                          v  Logs Run Metrics
                   +--------------+
                   |  MLflow Run  |
                   +--------------+
                          |
                          v  Promote Candidate
                  +----------------+
                  | Model Registry |
                  +----------------+
                          |
        +-----------------+-----------------+
        v                                   v
+---------------+                   +---------------+
|    Staging    |                   |  Production   |
| (Validation)  |                   | (Active API)  |
+---------------+                   +---------------+
```

### Model Registry Lifecycle
1.  **Candidate Registration**: The model matching our performance targets (ROC-AUC $\ge 0.85$, Recall $\ge 0.80$) is registered.
2.  **Staging Phase (`Staging`)**: The model undergoes integration testing, validating FastAPI schemas and inference latency ($<500$ ms).
3.  **Production Promotion (`Production`)**: Once approved, the candidate is promoted to the `Production` tag.
4.  **API Loading Logic**: On startup, the FastAPI server requests the latest model with the `Production` tag from the registry:
    ```python
    import mlflow.pyfunc
    model_uri = "models:/customer_churn_model/Production"
    model = mlflow.pyfunc.load_model(model_uri)
    ```

---

> [!TIP]
> Run the local MLflow dashboard using your terminal to compare candidate runs, evaluate validation loss curves, and inspect model registries:
> `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000`
