# Machine Learning Design Document
## Customer Intelligence & Retention Platform

| Field | Value |
| :--- | :--- |
| **Document Owner** | Rohil Verma |
| **Version** | 1.0 |
| **Created** | 2026-05-27 |
| **Status** | Approved for Development |

---

## Table of Contents
1. [ML Problem Formulation](#1-ml-problem-formulation)
2. [Feature Engineering & Preprocessing Pipeline](#2-feature-engineering--preprocessing-pipeline)
3. [Clustering Strategy (Layer 2)](#3-clustering-strategy-layer-2)
4. [Churn Prediction Strategy (Layer 3)](#4-churn-prediction-strategy-layer-3)
5. [Validation & Evaluation Strategy](#5-validation-&-evaluation-strategy)
6. [Explainability (SHAP) Specifications](#6-explainability-shap-specifications)

---

# 1. ML Problem Formulation

The platform's machine learning objective is divided into three distinct, layered modeling phases (descriptive, representation, and predictive analytics) that operate in series to construct the unified customer profile.

```
+---------------------------------------------------------------------------------+
|                                ML PIPELINE FLOW                                 |
|                                                                                 |
|  [Layer 1: RFM Scoring] --+                                                     |
|                           |                                                     |
|                           +---> [Layer 2: Representation & Density Clustering]  |
|                           |     - Standard Scaling                              |
|  [30+ Dense Features] ----+     - PyTorch Undercomplete Autoencoder             |
|                                 - Latent Bottleneck Embeddings (16D)            |
|                                 - HDBSCAN Density Clustering                    |
|                                           |                                     |
|                                           v                                     |
|                                 [Layer 3: Churn Prediction]                     |
|                                 - SMOTE Balancing                               |
|                                 - XGBoost Classifier                            |
|                                 - Optuna Hyperparameter Optimization            |
|                                 - SHAP Explainer (Explainability)               |
+---------------------------------------------------------------------------------+
```

### 1.1 Segmentation & Representation Learning (Layer 2)
*   **Type**: Unsupervised Representation Learning + Density-based Clustering.
*   **Input**: Standardized behavioral, RFM, and trend feature vectors.
*   **Target**: High-quality, low-dimensional latent representations (embeddings) that capture non-linear transaction patterns, followed by density clustering to group users showing similar shopping habits.

### 1.2 Churn Prediction (Layer 3)
*   **Type**: Supervised Binary Classification.
*   **Input**: Unified customer profiles (includes engineered features, RFM scores, and behavioral cluster IDs).
*   **Target Variable ($y$)**: Binary churn status.
    - $y = 1$: Customer has churned (inactive / zero purchases for $>60$ days).
    - $y = 0$: Active customer.
*   **Model Output**: Churn probability $\hat{p} \in [0, 1]$.

---

# 2. Feature Engineering & Preprocessing Pipeline

To prepare features for modeling, the raw feature matrix undergoes a multi-stage preprocessing pipeline.

```
       +-----------------------+
       |  Raw Feature Matrix   |
       +-----------------------+
                   |
                   v
       +-----------------------+
       |   Imputation Stage    | --> Numerical: Median | Categorical: "UNKNOWN"
       +-----------------------+
                   |
                   v
       +-----------------------+
       |    Encoding Stage     | --> Categorical: One-Hot / Target Encoders
       +-----------------------+
                   |
                   v
       +-----------------------+
       |     Scaling Stage     | --> Normal/Symmetric: StandardScaler
       |                       | --> Skewed Columns: RobustScaler
       +-----------------------+
                   |
                   v
       +-----------------------+
       |  Preprocessed Output  |
       +-----------------------+
```

### 2.1 Imputation Policy
*   **Skewed Numerical Fields** (e.g., `purchase_interval_avg`, `delivery_delay_tolerance_avg`): Imputed with the column median of the training split.
*   **Normally Distributed Fields** (e.g., `satisfaction_score_avg`): Imputed with the column mean.
*   **Categorical Fields**: Populated with the string `'UNKNOWN'` to prevent data loss.

### 2.2 Encoding Specification
*   **Low-Cardinality Categoricals** (e.g., `city_tier`, `gender`, `device_pref`): Encoded using One-Hot encoding.
*   **High-Cardinality Categoricals** (e.g., `payment_mode`): Encoded using Target Encoding based on the historical churn rate to avoid high-dimensional feature expansion.

### 2.3 Scaling Specification
*   **Normally Distributed Columns**: Scaled using standard normalization:
    $$z = \frac{x - \mu}{\sigma}$$
*   **Highly Skewed Columns** (e.g., total spend, transaction counts): Scaled using `RobustScaler` to minimize outlier influence:
    $$z = \frac{x - Q_2(x)}{Q_3(x) - Q_1(x)}$$

---

# 3. Clustering Strategy (Layer 2)

We compare a traditional clustering method with an advanced representation learning architecture.

### 3.1 Baseline: K-Means Clustering
*   **Input**: Standardized behavioral feature matrix.
*   **Distance Metric**: Euclidean distance.
*   **Optimization**: Elbow method (SSE) + Silhouette analysis to select the optimal number of clusters ($K$).

### 3.2 Advanced: Autoencoder + HDBSCAN

```
  Input Features (30+ Dimensions)
               |
               v   [Linear + ReLU Activation]
       Encoder Layer 1 (64 Dimensions)
               |
               v   [Linear + ReLU Activation]
       Encoder Layer 2 (32 Dimensions)
               |
               v   [Linear + ReLU Activation]
       Bottleneck Embedding (16 Dimensions)  <-- Latent Representation
               |
               v   [Linear + ReLU Activation]
       Decoder Layer 1 (32 Dimensions)
               |
               v   [Linear + ReLU Activation]
       Decoder Layer 2 (64 Dimensions)
               |
               v   [Linear + Sigmoid Activation]
  Output Reconstruction (30+ Dimensions)
```

#### Neural Network Configuration
- **Architecture**:
  - Input Layer: Size matches input features ($D \ge 30$).
  - Encoder: Dense(64, ReLU) $\rightarrow$ Dense(32, ReLU) $\rightarrow$ Bottleneck Dense(16, ReLU).
  - Decoder: Dense(32, ReLU) $\rightarrow$ Dense(64, ReLU) $\rightarrow$ Output Dense($D$, Sigmoid).
- **Optimization Strategy**:
  - Loss Function: Mean Squared Error (MSE) reconstruction loss.
  - Optimizer: Adam ($\eta = 10^{-3}$, weight decay $= 10^{-5}$).
  - Epochs: 150 with a batch size of 256. Early stopping halts training if the validation loss fails to improve for 10 consecutive epochs.

#### HDBSCAN Parameters
HDBSCAN is applied to the 16-dimensional bottleneck embeddings extracted from the trained Autoencoder:
- **Distance Metric**: Euclidean.
- **`min_cluster_size`**: 30 (ensures clusters represent meaningful customer segments).
- **`min_samples`**: 10 (controls cluster boundaries by restricting noise assignment).

---

# 4. Churn Prediction Strategy (Layer 3)

The classification pipeline is designed to predict churn probability.

### 4.1 Handling Class Imbalance
E-commerce churn datasets are typically imbalanced (often $>85\%$ active, $<15\%$ churned). The pipeline addresses this imbalance through:
1.  **SMOTE (Synthetic Minority Over-sampling Technique)**: Applied only to the training splits to generate synthetic instances of the churn class.
2.  **`scale_pos_weight`**: Set to the ratio of negative to positive samples:
    $$\text{scale\_pos\_weight} = \frac{N_{\text{active}}}{N_{\text{churned}}}$$

### 4.2 Algorithm Selection
*   **XGBoost Classifier (Primary Model)**: Chosen for its performance on structured tabular data, built-in support for missing value splitting, regularization parameters, and scalability.
*   **Random Forest Classifier (Baseline Model)**: A bagging ensemble baseline to evaluate performance gains.

### 4.3 Hyperparameter Optimization
**Optuna** is used to run 50 trials of Bayesian optimization over the 5-fold cross-validation split, searching the following hyperparameter spaces:

| Hyperparameter | Type | Search Range |
| :--- | :--- | :--- |
| `max_depth` | Integer | [3, 10] |
| `learning_rate` | Float | [0.01, 0.20] |
| `n_estimators` | Integer | [100, 1000] |
| `min_child_weight` | Integer | [1, 10] |
| `subsample` | Float | [0.6, 1.0] |
| `colsample_bytree` | Float | [0.6, 1.0] |
| `gamma` | Float | [0.0, 5.0] |

---

# 5. Validation & Evaluation Strategy

To prevent data leakage and ensure model generalization, we implement a strict validation framework.

```
       +--------------------------------------------+
       |            Complete Dataset                |
       +--------------------------------------------+
                             |
                   +---------+---------+
                   v                   v
             +-----------+       +-----------+
             |   Train   |       |   Test    |  (Hold-out Test Split: 20%)
             +-----------+       +-----------+
                   |                   |
                   v                   |  (Evaluate Final Model)
             +-----------+             |
             |  5-Fold   |             |
             | Stratified|             |
             |    CV     |             |
             +-----------+             |
                   |                   |
                   v                   v
         +-----------------------------------+
         |         Model Performance         |
         +-----------------------------------+
```

### 5.1 Split Specification
*   **Hold-out Test Split**: 20% of the raw customer feature records are held out for final evaluation.
*   **Cross-Validation**: The remaining 80% of the dataset is processed using 5-Fold Stratified Cross-Validation to ensure consistent class distributions across all folds.

### 5.2 Model Metrics & Performance Targets
*   **Primary Metric**: Area Under the ROC Curve (ROC-AUC).
*   **Secondary Metrics**:
  - **Recall**: Crucial for churn prediction; ensures the business captures the majority of customers at risk.
  - **F1-Score**: Evaluates performance balance on imbalanced datasets.
*   **Performance Thresholds**:
  - Churn Prediction (XGBoost): ROC-AUC $\ge$ 0.85, Recall $\ge$ 0.80, F1-Score $\ge$ 0.75.
  - Clustering (Autoencoder + HDBSCAN): Silhouette Score $\ge$ 0.35.

---

# 6. Explainability (SHAP) Specifications

Explainability is built directly into the core modeling layer using SHAP (SHapley Additive exPlanations) to interpret predictions.

### 6.1 SHAP Explainer Initialization
- **Explainer Engine**: `shap.TreeExplainer` (optimized for tree-based models like XGBoost).
- **Background Dataset**: To ensure quick API response times ($<500$ ms), we pass a representative background dataset of 100 customer profiles constructed from K-Means cluster centroids.

### 6.2 Visualizations and Explanations
The dashboard utilizes three primary visualizations to explain model predictions:
1.  **Global Interpretability**: A Beeswarm plot displaying the top 15 features sorted by their mean absolute SHAP values, showing global feature impact on churn.
2.  **Local Interpretability**: A Waterfall plot displaying feature contributions for individual customer lookups, explaining the specific factors driving that prediction.
3.  **Feature Interactions**: Dependence plots for the top 5 features to identify non-linear relationships and decision boundaries.

---

> [!WARNING]
> SMOTE must only be applied to the training fold of each cross-validation split. Applying SMOTE to the validation fold or the hold-out test set introduces data leakage, resulting in inflated performance metrics.
