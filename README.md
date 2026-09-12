# ChurnGuard AI

> **Explainable Customer Churn Prediction & Retention Intelligence Platform**

ChurnGuard AI is an end-to-end machine learning application that predicts whether a customer is likely to churn, estimates their churn probability, identifies the strongest risk factors, and generates actionable retention recommendations.

Built with **Python, Flask, Scikit-learn, XGBoost, LightGBM, SHAP, JavaScript, Chart.js and Three.js**.

---

## ✨ Highlights

* 🎯 **Customer-level churn prediction**
* 📊 **5 ML algorithms + stacking ensemble**
* 🧠 **SHAP-powered explainability**
* ⚙️ **30 predictive features** from 20 raw inputs
* 🔄 **SMOTE** for class-imbalance handling
* 📈 ROC-AUC, F1, Precision, Recall & Accuracy evaluation
* 💡 Automated retention recommendations
* 🚦 Low → Critical risk classification
* 🔌 REST API with Flask
* 📦 Batch prediction support
* 📊 Interactive analytics dashboard
* 🌌 Modern glassmorphism + animated Three.js interface

---

## 🧩 System Architecture

```text
                    ┌─────────────────────┐
                    │     Web Frontend    │
                    │ HTML/CSS/JS/Charts  │
                    └──────────┬──────────┘
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │     Flask Backend   │
                    │ Prediction Engine   │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
       Feature Engineering  Preprocessing    Trained Models
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Stacking Ensemble   │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Probability + Risk  │
                    │ SHAP + Recommendations│
                    └─────────────────────┘
```

---

# 🤖 Machine Learning Pipeline

```text
Raw Customer Data
       ↓
Data Validation & EDA
       ↓
Feature Engineering
       ↓
Categorical Encoding
       ↓
Robust Scaling
       ↓
Train/Test Split
       ↓
SMOTE on Training Data
       ↓
Model Training
       ↓
5-Fold Cross Validation
       ↓
Model Comparison
       ↓
Stacking Ensemble
       ↓
Prediction + Explainability
```

---

# 📊 Dataset

The project uses a **synthetic telecom/SaaS customer dataset containing 10,000 records**.

| Property            |  Value |
| ------------------- | -----: |
| Samples             | 10,000 |
| Raw Features        |     20 |
| Engineered Features |     10 |
| Final Features      |     30 |
| Target              |  Churn |
| Churn Rate          | 55.99% |
| Non-Churn Rate      | 44.01% |

The dataset is generated locally using `generate_data.py` and is intentionally excluded from GitHub through `.gitignore`.

---

# 🧬 Input Features

### Customer Profile

| Feature          | Description                     |
| ---------------- | ------------------------------- |
| `age`            | Customer age                    |
| `gender`         | Customer gender                 |
| `has_partner`    | Whether customer has a partner  |
| `has_dependents` | Whether customer has dependents |

### Subscription & Revenue

| Feature           | Description                          |
| ----------------- | ------------------------------------ |
| `tenure_months`   | Customer lifetime in months          |
| `contract_type`   | Month-to-Month, One-Year or Two-Year |
| `monthly_charges` | Recurring monthly charges            |
| `total_charges`   | Total customer charges               |
| `num_products`    | Number of subscribed products        |
| `discount_pct`    | Applied discount percentage          |

### Engagement

| Feature                       | Description                      |
| ----------------------------- | -------------------------------- |
| `days_since_last_interaction` | Days since last interaction      |
| `avg_session_duration_min`    | Average session duration         |
| `login_frequency_monthly`     | Monthly login frequency          |
| `feature_usage_rate`          | Product feature usage percentage |

### Support & Satisfaction

| Feature               | Description                    |
| --------------------- | ------------------------------ |
| `num_support_tickets` | Number of support tickets      |
| `satisfaction_score`  | Customer satisfaction score    |
| `nps_score`           | Net Promoter Score             |
| `referral_count`      | Number of successful referrals |

### Payment

| Feature          | Description              |
| ---------------- | ------------------------ |
| `payment_method` | Customer payment method  |
| `payment_delays` | Number of payment delays |

---

# ⚙️ Feature Engineering

20 raw inputs are transformed into **30 model-ready features**.

| Engineered Feature       | Purpose                                          |
| ------------------------ | ------------------------------------------------ |
| `charge_per_tenure`      | Revenue intensity over tenure                    |
| `total_charge_ratio`     | Actual vs expected lifetime charges              |
| `support_per_tenure`     | Support burden relative to tenure                |
| `engagement_score`       | Combined usage/engagement indicator              |
| `tenure_group`           | Customer lifecycle segmentation                  |
| `clv_proxy`              | Approximate customer lifetime value              |
| `satisfaction_nps_ratio` | Satisfaction-to-NPS relationship                 |
| `inactivity_score`       | Inactivity adjusted for login frequency          |
| `payment_risk`           | Financial risk indicator                         |
| `loyalty_score`          | Tenure, referrals, products and payment behavior |

Example:

```text
engagement_score =
    0.3 × login_frequency
  + 0.3 × session_duration
  + 0.4 × feature_usage
```

---

# 🛠️ Preprocessing

The training pipeline includes:

* Stratified train/test split
* Median numerical imputation
* Label encoding for categorical variables
* `RobustScaler` for numerical normalization
* SMOTE for training-set class balancing
* 5-fold cross-validation
* Consistent preprocessing during inference

SMOTE increases representation of the minority class so models are less biased toward the majority class.

---

# 🧠 Models

Five individual models are evaluated:

1. **Logistic Regression**
2. **Random Forest**
3. **Gradient Boosting**
4. **XGBoost**
5. **LightGBM**

A **Stacking Ensemble** combines:

```text
Random Forest
      +
XGBoost
      +
LightGBM
      ↓
Logistic Regression Meta-Model
```

The final model is selected using:

```text
Composite Score =
0.6 × ROC-AUC + 0.4 × F1
```

---

# 📈 Model Performance

| Model                 |   Accuracy |  Precision |     Recall |         F1 |    ROC-AUC |
| --------------------- | ---------: | ---------: | ---------: | ---------: | ---------: |
| Logistic Regression   |     64.35% |     69.18% |     65.54% |     67.31% | **70.36%** |
| Random Forest         | **65.40%** |     67.77% |     72.86% |     70.22% |     69.73% |
| Gradient Boosting     |     63.90% |     66.18% |     72.68% |     69.28% |     68.21% |
| XGBoost               |     63.60% |     67.85% |     66.52% |     67.18% |     68.21% |
| LightGBM              |     63.95% |     68.46% |     66.07% |     67.24% |     68.54% |
| **Stacking Ensemble** | **65.10%** | **66.54%** | **75.80%** | **70.87%** | **69.71%** |

### 🏆 Selected Model

**Stacking Ensemble**

* Accuracy: **65.10%**
* F1: **70.87%**
* ROC-AUC: **69.71%**
* Recall: **75.80%**

The ensemble provides strong recall, making it useful when identifying potentially lost customers is more important than minimizing false positives.

---

# 🔍 Explainable AI — SHAP

ChurnGuard uses **SHAP (SHapley Additive exPlanations)** to understand which features contribute most strongly to predictions.

### Top Predictive Features

| Feature                    | SHAP Importance |
| -------------------------- | --------------: |
| `satisfaction_score`       |           0.286 |
| `discount_pct`             |           0.249 |
| `contract_type`            |           0.221 |
| `loyalty_score`            |           0.184 |
| `monthly_charges`          |           0.161 |
| `support_per_tenure`       |           0.150 |
| `inactivity_score`         |           0.139 |
| `feature_usage_rate`       |           0.135 |
| `nps_score`                |           0.119 |
| `avg_session_duration_min` |           0.112 |

This makes the model more interpretable than simply returning a binary churn prediction.

---

# 🚦 Risk Classification

Predicted probability is converted into an operational risk level:

| Probability | Risk        |
| ----------: | ----------- |
|     `< 30%` | 🟢 Low      |
|    `30–59%` | 🟡 Medium   |
|    `60–79%` | 🟠 High     |
|     `≥ 80%` | 🔴 Critical |

The API also returns a confidence score based on the distance of the probability from the decision threshold.

---

# 💡 Retention Intelligence

The application doesn't stop at:

> **"This customer may churn."**

It also generates potential retention actions based on customer behavior.

Examples:

* Recommend annual contracts
* Offer targeted discounts
* Address low satisfaction
* Reduce support friction
* Re-engage inactive customers
* Increase product adoption
* Address payment issues
* Introduce referral incentives

This turns the project from a simple classifier into a **churn decision-support system**.

---

# 🔌 REST API

### Predict Customer Churn

```http
POST /api/predict
```

Returns:

```json
{
  "prediction": {
    "churn_prediction": 0,
    "churn_probability": 0.4968,
    "confidence": 0.0063,
    "risk_level": "Medium"
  },
  "risk_factors": [],
  "recommendations": [],
  "success": true
}
```

### Other Endpoints

| Endpoint                   | Purpose                                |
| -------------------------- | -------------------------------------- |
| `GET /api/model-info`      | Model information & feature importance |
| `POST /api/predict`        | Individual prediction                  |
| `POST /api/batch-predict`  | Multiple customer predictions          |
| `GET /api/dashboard-stats` | Dashboard/model statistics             |

---

# 🖥️ Frontend

The web interface provides:

* Executive KPI dashboard
* Customer prediction form
* Risk gauge
* Risk-factor visualization
* Retention recommendations
* Model comparison charts
* Feature importance visualization
* Analytics section
* Interactive model pipeline
* Animated Three.js background

### Frontend Stack

```text
HTML5
CSS3
JavaScript
Chart.js
Three.js
GSAP
```

---

# 📁 Project Structure

```text
Churn App/
│
├── Backend/
│   ├── app.py
│   ├── churn_model.py
│   ├── generate_data.py
│   ├── requirements.txt
│   │
│   ├── data/              # generated dataset — ignored
│   └── saved_models/      # trained artifacts — ignored
│
├── Frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── app.js
│       ├── charts.js
│       └── three-scene.js
│
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

### 1. Clone

```bash
git clone <repository-url>
cd "Churn App"
```

### 2. Create virtual environment

```bash
cd Backend
python -m venv venv
```

### 3. Activate

Windows:

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

### 5. Generate dataset

```cmd
python generate_data.py
```

### 6. Train models

```cmd
python churn_model.py
```

### 7. Start API

```cmd
python app.py
```

Open:

```text
http://localhost:5000
```

---

# 🧪 Reproducibility

The repository keeps the **source code and training pipeline** under version control while excluding generated datasets, trained model artifacts, virtual environments and local IDE files.

To reproduce the ML artifacts:

```text
generate_data.py
       ↓
churn_model.py
       ↓
saved_models/
```

---

# ⚠️ Limitations

This project is designed as an **ML engineering and demonstration system**.

* Dataset is synthetic.
* Performance will differ on real-world customer data.
* Predictions should not be treated as guaranteed outcomes.
* The current pipeline prioritizes practical demonstration over production-scale MLOps.
* Model performance can be improved through real customer data, hyperparameter optimization and more advanced categorical preprocessing.

---

# 🔮 Future Improvements

* Real-world telecom/e-commerce datasets
* One-hot/target encoding improvements
* SMOTENC for mixed feature types
* Hyperparameter optimization
* Model calibration
* Advanced threshold optimization
* Real-time monitoring
* Model drift detection
* Database integration
* Authentication & role-based access
* Cloud deployment
* Automated retraining
* Production MLOps pipeline

---

# 🧰 Technology Stack

**Machine Learning**

`Python` · `Pandas` · `NumPy` · `Scikit-learn` · `XGBoost` · `LightGBM` · `imbalanced-learn` · `SHAP`

**Backend**

`Flask` · `Flask-CORS` · `Joblib`

**Frontend**

`HTML` · `CSS` · `JavaScript` · `Chart.js` · `Three.js` · `GSAP`

**Development**

`Git` · `GitHub` · `VS Code / Visual Studio`

---

## 👨‍💻 Author

**Anas Adeel**

Artificial Intelligence Student · ML & AI Developer

---

## 📄 License

This project is intended for educational, portfolio and demonstration purposes.
