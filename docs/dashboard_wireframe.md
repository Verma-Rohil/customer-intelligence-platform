# Dashboard Wireframe Document
## Customer Intelligence & Retention Platform

| Field | Value |
| :--- | :--- |
| **Document Owner** | Rohil Verma |
| **Version** | 1.0 |
| **Created** | 2026-05-27 |
| **Status** | Approved for Development |
| **UI Framework** | React 19 + Vite (SPA) |
| **Theme** | Premium Dark Mode (Slate Grey background `#0E1117`, Emerald green highlights `#10B981`) |

---

## Table of Contents
1. [User Interface Design System](#1-user-interface-design-system)
2. [Page 1: Executive Overview](#2-page-1-executive-overview)
3. [Page 2: Customer Lookup (SHAP Focus)](#3-page-2-customer-lookup-shap-focus)
4. [Page 3: Segment Deep Dive](#4-page-3-segment-deep-dive)
5. [Page 4: Segment Migration over Time](#5-page-4-segment-migration-over-time)
6. [Page 5: Campaign Simulator (ROI Focus)](#6-page-5-campaign-simulator-roi-focus)
7. [Page 6: Model Performance Metrics](#7-page-6-model-performance-metrics)

---

# 1. User Interface Design System

The platform's frontend dashboard is built with React and Vite. The layout features a consistent React Router Sidebar component for page navigation and global filters, while the main canvas displays responsive CSS grids and Framer Motion animations.

### Color Palette & Style Guidelines
*   **Background**: Slate/Dark Charcoal (`#0E1117`) to create a professional analytics interface.
*   **Cards**: Dark Grey (`#1E222B`) with rounded corners and subtle shadow borders.
*   **Accents**: Emerald Green (`#10B981`) to indicate positive values and low risk; Amber (`#F59E0B`) for medium risk; Coral Red (`#EF4444`) for churn risk alerts and negative trends.
*   **Charts**: Interactive Plotly charts with transparent backgrounds and matching dark theme templates (`plotly_dark`).

---

# 2. Page 1: Executive Overview

This page provides executive-level context, showing overall business health, active customer counts, average churn rate, and total revenue contribution.

```
+-----------------------------------------------------------------------------------+
|  [Sidebar: Page Selection]              📊 EXECUTIVE OVERVIEW                    |
|  (o) Executive Overview                                                           |
|  ( ) Customer Lookup         +-------------------------------------------------+  |
|  ( ) Segment Deep Dive       |  KPI CARDS                                      |  |
|  ( ) Segment Migration       |  [Active Customers]   [Overall Churn Rate]       |  |
|  ( ) Campaign Simulator      |  85,000 (▲ 2.1%)      12.4% (▼ 0.5%)            |  |
|  ( ) Model Performance       |                                                 |  |
|                              |  [High-Risk Customers] [Avg Customer Lifetime]  |  |
|                              |  10,540 (Alert!)       ₹5,200.00 (Flat)         |  |
|                              +-------------------------------------------------+  |
|                                                                                   |
|  +---------------------------------------+  +----------------------------------+  |
|  | Donut: Segment Distribution          |  | Bar: Spend by Customer Segment   |  |
|  |                                       |  |                                  |  |
|  |        Champions (35%)                |  | Champions  |███████████████      |  |
|  |       /               \               |  | Loyal Cust |████████████          |  |
|  |   Loyal (25%)       At Risk (15%)     |  | Recent Buy |██████                |  |
|  |       \               /               |  | At Risk    |████                  |  |
|  |      Others (15%)  Lost (10%)         |  | Lost/Hiber |██                    |  |
|  +---------------------------------------+  +----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Component Logic & Plotly Config
*   **KPI Cards**: Constructed using reusable React components with delta indicators showing changes compared to the prior month's snapshot.
*   **Donut Chart**: Built using `plotly.js` via a wrapper component with a specified `hole=0.4` and mapped segment colors.
*   **Stacked Spend Bar Chart**: Displays total spend values on the X-axis and segment categories on the Y-axis.

---

# 3. Page 2: Customer Lookup (SHAP Focus)

This page allows account managers to look up specific customer profiles, view their individual churn risk probability, analyze underlying behavioral drivers, and get recommended actions.

```
+-----------------------------------------------------------------------------------+
|  [Sidebar: Page Selection]              🔍 CUSTOMER LOOKUP ENGINE                 |
|  ( ) Executive Overview                                                           |
|  (o) Customer Lookup         Search Customer: [ USR-98402           ] [ Search ]  |
|  ( ) Segment Deep Dive                                                            |
|  ( ) Segment Migration       +-------------------------------------------------+  |
|  ( ) Campaign Simulator      | CUSTOMER PROFILE SUMMARY                        |  |
|  ( ) Model Performance       | - RFM Segment: At Risk      - Cluster: Discount |  |
|                              | - Tenure: 14 Months         - Complaints: 2     |  |
|                              +-------------------------------------------------+  |
|                                                                                   |
|  +---------------------------+  +----------------------------------------------+  |
|  | Gauge: Churn Probability  |  | Recommended Retention Strategy               |  |
|  |                           |  |                                              |  |
|  |          78.0%            |  | > Flat 20% Discount Coupon (Value: ₹500)      |  |
|  |       /         \         |  | > Personal Outreach Call from Support Team   |  |
|  |   [0% === 50% === 100%]   |  |                                              |  |
|  |        (HIGH RISK)        |  | Expected Success Probability: 72%            |  |
|  +---------------------------+  +----------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | SHAP Waterfall: Feature Contributions to Prediction                         |  |
|  |                                                                             |  |
|  | Base Value (0.12) ----> [Login Recency (+0.32)] ----> [Complaints (+0.18)]  |  |
|  |                   ----> [Satisfaction (-0.11)]  ----> Churn Prob: 78.0%     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Component Logic & Plotly Config
*   **Churn Probability Gauge**: Built using `plotly.js` with the gauge indicator mode enabled, displaying color transitions from green ($0\%$) to red ($100\%$).
*   **SHAP Bar Chart**: Renders horizontal bar charts representing SHAP values fetched from the FastAPI backend.

---

# 4. Page 3: Segment Deep Dive

This page is designed for database profiling. It provides feature distribution breakdowns and compares K-Means clustering with our Autoencoder + HDBSCAN pipeline.

```
+-----------------------------------------------------------------------------------+
|  [Sidebar: Page Selection]              🎯 SEGMENT DEEP DIVE                      |
|  ( ) Executive Overview                                                           |
|  ( ) Customer Lookup         Select Segment Category: [ At Risk                  ]  |
|  (o) Segment Deep Dive                                                            |
|  ( ) Segment Migration       +-------------------------------------------------+  |
|  ( ) Campaign Simulator      | Cluster Profile Statistics (Mean Values)        |  |
|  ( ) Model Performance       | Metric       Segment Mean       Population Mean |  |
|                              | Recency      45 days            18 days         |  |
|                              | Spend        ₹4,120.00          ₹5,400.00       |  |
|                              +-------------------------------------------------+  |
|                                                                                   |
|  +---------------------------------------+  +----------------------------------+  |
|  | Scatter: K-Means Clusters             |  | Scatter: AE + HDBSCAN Clusters   |  |
|  | (UMAP Projection Space)               |  | (Bottleneck Projection Space)    |  |
|  |  *  *    +  +  +                      |  |   **    +++     ####             |  |
|  | *  *  *  +  +  +                      |  |  ***   ++++    #####             |  |
|  |  *  *    +  +  +                      |  |   **    +++     ####             |  |
|  | Silhouette Score: 0.38                |  | Silhouette Score: 0.52           |  |
|  +---------------------------------------+  +----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Component Logic & Plotly Config
*   **Profile Comparison Table**: Built with React data tables or grid layouts, comparing the selected segment's feature averages against the overall customer population.
*   **Side-by-Side Scatter Plots**: Renders 3D scatter plots for PCA/UMAP dimensionality reduction coordinates. Points are colored dynamically by cluster ID.

---

# 5. Page 4: Segment Migration over Time

Tracks changes in customer cohorts across sequential months, displaying customer retention flows and segment migration paths.

```
+-----------------------------------------------------------------------------------+
|  [Sidebar: Page Selection]              📈 SEGMENT MIGRATION OVER TIME            |
|  ( ) Executive Overview                                                           |
|  ( ) Customer Lookup         Select Snapshot Interval: [ Month 1 -> Month 2 ]      |
|  ( ) Segment Deep Dive                                                            |
|  (o) Segment Migration       +-------------------------------------------------+  |
|  ( ) Campaign Simulator      | Key Migrations Tracker                          |  |
|  ( ) Model Performance       | [Warning] 180 Champions migrated to At Risk!    |  |
|                              | [Success] 340 At Risk migrated to Loyal!        |  |
|                              +-------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Sankey Flow Diagram: Segment Transitions                                    |  |
|  |                                                                             |  |
|  |  Month 1 Segments                     Flows                 Month 2 Segments|  |
|  |  [ Champions ] ==========================================> [ Champions ]    |  |
|  |  [ Loyal     ] ============ \                 / ==========> [ Loyal     ]    |  |
|  |  [ At Risk   ] ============  \               /  ==========> [ At Risk   ]    |  |
|  |  [ Lost      ] =============  =======> ====== =============> [ Lost      ]    |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Component Logic & Plotly Config
*   **Sankey Diagram**: Built using `plotly.graph_objects.Sankey`. Node and link parameters map Month 1 segment positions (sources) to Month 2 segment positions (targets).

---

# 6. Page 5: Campaign Simulator (ROI Focus)

Provides an interactive sandbox interface for marketing managers to select customer segments and campaign types, estimating retention costs and return on investment (ROI).

```
+-----------------------------------------------------------------------------------+
|  [Sidebar: Page Selection]              💰 CAMPAIGN SIMULATOR ENGINE              |
|  ( ) Executive Overview                                                           |
|  ( ) Customer Lookup         Target Segment:   [ At Risk                       ]  |
|  ( ) Segment Deep Dive       Select Campaign:  [ C1: Flat 20% Discount Coupon  ]  |
|  ( ) Segment Migration       Cost Override:    [ None (Default: ₹500/User)     ]  |
|  (o) Campaign Simulator                                                           |
|  ( ) Model Performance       +-------------------------------------------------+  |
|                              | SIMULATION ROI RESULTS                          |  |
|                              | [Total Cost]  [Saved Users]  [Projected Revenue]|  |
|                              | ₹125,000.00   75 Users       ₹300,000.00        |  |
|                              |                                                 |  |
|                              | Projected Net ROI (%): 140.0% (PROCEED)         |  |
|                              +-------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Bar: Campaign ROI Comparison Matrix                                         |  |
|  |                                                                             |  |
|  |   ROI (%)                                                                   |  |
|  |    200% |       ██                                                          |  |
|  |    100% |       ██             ██                                           |  |
|  |      0% |       ██             ██             ██                            |  |
|  |         +--------------+--------------+--------------+                       |  |
|  |          Flat 20% Disc   Loyalty Pts   Onboard Email                        |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Component Logic & Plotly Config
*   **ROI Metrics Grid**: Dynamically displays simulated values calculated from segment sizes, CLVs, and campaign costs using formulas defined in the System Design.
*   **ROI Bar Chart**: A Plotly express bar chart (`px.bar`) comparing net ROI percentages across all campaign types for the selected segment.

---

# 7. Page 6: Model Performance Metrics

A monitoring page displaying evaluation metrics, confusion matrices, and ROC curves to help engineering teams track model stability and accuracy.

```
+-----------------------------------------------------------------------------------+
|  [Sidebar: Page Selection]              🏆 MODEL PERFORMANCE METRICS              |
|  ( ) Executive Overview                                                           |
|  ( ) Customer Lookup         Active Model: [ XGBoost Classifier v1.0 ]            |
|  ( ) Segment Deep Dive                                                            |
|  ( ) Segment Migration       +-------------------------------------------------+  |
|  ( ) Campaign Simulator      | Model Metric Leaderboard                        |  |
|  (o) Model Performance       | Algorithm     ROC-AUC    F1-Score  Recall       |  |
|                              | XGBoost       0.92       0.82      0.83         |  |
|                              | Random Forest 0.88       0.78      0.79         |  |
|                              | Logistic Reg. 0.82       0.71      0.72         |  |
|                              +-------------------------------------------------+  |
|                                                                                   |
|  +---------------------------------------+  +----------------------------------+  |
|  | Line: ROC Curves Comparison           |  | Heatmap: Confusion Matrix        |  |
|  |                                       |  |                                  |  |
|  | TPR                                   |  |               Predicted          |  |
|  | 1.0 |       /  (XGBoost: 0.92)        |  |               No       Yes       |  |
|  | 0.5 |     /                           |  | Actual  No  [ 15,200 ] [  340 ]  |  |
|  | 0.0 +----------------                 |  |        Yes  [   120 ] [ 1,540 ]  |  |
|  |    0.0     0.5     1.0  FPR           |  |                                  |  |
|  +---------------------------------------+  +----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Component Logic & Plotly Config
*   **ROC / PR Curve Overlay**: Built using Plotly lines to render comparison curves for candidate models on the same axes.
*   **Feature Importance**: A horizontal bar chart displaying top features natively extracted from the XGBoost model via FastAPI.

---

> [!TIP]
> The React app fetches data asynchronously from the FastAPI service. Ensure `fetch` responses are handled gracefully with loading spinners and error boundaries.
