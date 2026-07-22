# 🫀 Heart Disease Prediction Engine
### Real Clinical Data · SVM · Logistic Regression · Threshold Optimization

---

## 📌 Business Problem

> *"Given a patient's medical test results — can we predict whether they have heart disease before invasive procedures?"*

Heart disease is the leading cause of death globally. Early detection through non-invasive testing saves lives. This project builds a Machine Learning model trained on real Cleveland Clinic data to predict heart disease from routine medical tests.

---

## 🎯 Objective

| | |
|--|--|
| **Input** | Age, sex, chest pain type, blood pressure, cholesterol, heart rate, ECG results, and more |
| **Output** | 0 = No heart disease, 1 = Heart disease detected |
| **Selected Model** | Logistic Regression (Tuned) + Threshold 0.55 |
| **Dataset** | Cleveland Heart Disease — UCI Repository (279 rows after cleaning) |

---

## 📊 Dataset

| Property | Value |
|----------|-------|
| Source | Cleveland Clinic — UCI Repository (Kaggle) |
| Original rows | 297 |
| Rows after outlier removal | 279 |
| Raw features | 13 |
| Features after One Hot Encoding | 18 |
| Target | `condition` (0 = healthy, 1 = heart disease) |
| Class balance | 55% healthy, 45% disease |

### Feature Dictionary

| Feature | Description | Type |
|---------|-------------|------|
| age | Age in years | Numeric |
| sex | 0 = female, 1 = male | Binary |
| cp | Chest pain type (0,1,2,3) | Categorical → One Hot |
| trestbps | Resting blood pressure (mm Hg) | Numeric |
| chol | Cholesterol (mg/dl) | Numeric |
| fbs | Fasting blood sugar > 120 mg/dl | Binary |
| restecg | Resting ECG results (0,1,2) | Categorical → One Hot |
| thalach | Maximum heart rate achieved | Numeric |
| exang | Exercise induced angina (0/1) | Binary |
| oldpeak | ST depression induced by exercise | Numeric |
| slope | Slope of peak exercise ST (0,1,2) | Categorical → One Hot |
| ca | Number of major vessels (0-3) | Numeric |
| thal | Thalassemia type (0,1,2) | Categorical → One Hot |

---

## 🧹 Data Cleaning Pipeline

| Step | Action |
|------|--------|
| Missing values | Zero missing — clean dataset |
| Outlier detection | BoxPlot visual inspection on trestbps, chol, oldpeak |
| Outlier removal | IQR method — removed 18 rows |
| Skewness check | chol (1.12) and oldpeak (1.25) — resolved after IQR removal |
| Duplicates | None found |
| KDE analysis | thalach and oldpeak show strongest separation between disease/healthy |

---

## ⚙️ Feature Engineering & Encoding

| Step | Method | Details |
|------|--------|---------|
| One Hot Encoding | `ColumnTransformer` + `OneHotEncoder` | cp, restecg, slope, thal (drop_first=True) |
| Encoding order | `fit_transform` on train, `transform` on test | Zero leakage |
| Multicollinearity | Custom correlation function (threshold=0.85) | No correlated pairs found |
| Feature scaling | `StandardScaler` | Mandatory for SVM — distance-based model |

---

## 📈 Model Performance — All 6 Models

| Model | Accuracy | Recall (Disease) | AUC |
|-------|----------|-----------------|-----|
| SVC Linear | 0.8571 | 0.7200 | 0.9394 |
| SVC RBF | 0.8393 | 0.8000 | 0.9110 |
| SVC Polynomial | 0.8214 | 0.6400 | 0.9316 |
| Logistic Regression | 0.8571 | 0.7200 | 0.9445 |
| SVC RBF Tuned | 0.8571 | 0.7200 | 0.9419 |
| **LR Tuned** | **0.8393** | **0.9600** | **0.9458** |

---

## 🏆 Model Selection — LR Tuned

### Why LR Tuned was selected over SVC RBF Tuned

```
SVC RBF Tuned  →  Accuracy 0.86  Recall 0.72  →  misses 7/25 sick patients
LR Tuned       →  Accuracy 0.84  Recall 0.96  →  misses only 1/25 sick patient

In healthcare : missing a sick patient = no treatment = possible death
A false alarm  = extra test = minor inconvenience

6 more sick patients caught is worth the 2% accuracy drop
```

### Threshold Optimization

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|-----|
| 0.30 | 1.00 | 0.64 | 0.78 |
| 0.40 | 1.00 | 0.69 | 0.82 |
| 0.50 | 0.96 | 0.71 | 0.81 |
| **0.55** | **0.96** | **0.75** | **0.84** |
| 0.60 | 0.88 | 0.79 | 0.83 |

**Selected threshold: 0.55** (Youden's J = 0.7665)

### Final Results at Threshold 0.55

```
Disease caught  : 24 / 25  (96.0%)
Disease missed  :  1 / 25  ( 4.0%)
False alarms    :  8 / 31  (25.8%)
Precision       : 0.75
AUC             : 0.9458
```

---

## 🔑 Key Clinical Insights from EDA

### Feature Separation (KDE Analysis)

```
thalach (max heart rate) → strongest separation
    Disease patients have LOWER max heart rate than healthy
    
oldpeak (ST depression) → strong separation
    Disease patients have HIGHER ST depression
    
chol (cholesterol) → weak separation
    Curves overlap — cholesterol alone is not a reliable indicator
    
trestbps (blood pressure) → weak separation
    High BP is a risk factor but not a strong differentiator
```

### Chest Pain Type

```
cp = 3 (asymptomatic) → highest rate of heart disease
    Patients who feel NO chest pain often have blocked arteries
    This is a known medical finding
```

---

## 🗂️ Project Structure

```
heart_disease_prediction/
│
├── heart_cleveland_upload.csv      ← dataset
├── Heart_Disease_Prediction.ipynb  ← full ML pipeline
├── app.py                          ← Flask web app
├── models/
│   ├── svc_linear.pkl
│   ├── svc_rbf.pkl
│   ├── svc_poly.pkl
│   ├── lr_basic.pkl
│   ├── svc_rbf_tuned.pkl
│   ├── lr_tuned.pkl               ← BEST MODEL
│   ├── scaler.pkl
│   ├── column_transformer.pkl
│   ├── feature_columns.pkl
│   └── threshold.pkl              ← 0.55
├── templates/
│   ├── index.html
│   └── result.html
└── README.md
```

---

## 🔧 Tech Stack

| Tool | Usage |
|------|-------|
| Python 3.10 | Core language |
| Pandas / NumPy | Data cleaning and feature engineering |
| Seaborn / Matplotlib | EDA, BoxPlots, KDE, ROC curves |
| Scikit-Learn | SVC, LogisticRegression, StandardScaler, OneHotEncoder, ColumnTransformer, RandomizedSearchCV |
| Flask | Web application for live predictions |
| Pickle | Model serialization |

---

## 🚀 How to Run

### Notebook

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
jupyter notebook Heart_Disease_Prediction.ipynb
# Kernel → Restart & Run All
```

### Flask App

```bash
cd heart_disease_prediction
pip install flask
python app.py
# Open http://127.0.0.1:5000
```

---

## 📄 Resume Bullet Points

```
• Built a Heart Disease Prediction Engine on real Cleveland Clinic data
  (279 patients) using SVM (3 kernels) and Logistic Regression

• Applied full industry pipeline: IQR outlier removal, skewness analysis,
  KDE feature separation, ColumnTransformer with OneHotEncoder,
  StandardScaler, and multicollinearity detection

• Compared 6 models — selected LR Tuned (AUC 0.9458) over SVC RBF Tuned
  (AUC 0.9419) because LR catches 24/25 sick patients vs SVC catching 18/25

• Optimized decision threshold from 0.50 to 0.55 using Youden's J statistic
  achieving 96% recall with 75% precision on heart disease detection

• Deployed as Flask web app with pickled models, scaler, and
  ColumnTransformer for production-ready live predictions
```

---

## 🔮 Future Improvements

| Improvement | Expected Impact |
|------------|----------------|
| Feature selection using RFE or SelectKBest | Remove weak features, reduce overfitting |
| Ensemble methods (Random Forest, XGBoost) | Likely better accuracy on small datasets |
| Cross-validation on threshold selection | More robust threshold choice |
| Larger dataset (combine with Hungarian + Swiss) | More training data = better generalization |
| Streamlit deployment | More interactive UI for clinicians |

---

*Dataset: Cleveland Heart Disease — UCI Repository (Kaggle)*
*Built for portfolio and learning purposes*