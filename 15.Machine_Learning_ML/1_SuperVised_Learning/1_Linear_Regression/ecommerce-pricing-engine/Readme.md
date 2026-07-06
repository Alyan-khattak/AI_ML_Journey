# 🛒 Amazon India — Product Price Prediction Engine
### Real Scraped Data · Multiple Linear Regression · Polynomial Regression · Python

---

## 📌 Business Problem

Every Amazon India seller faces the same question daily:

> *"Given my product's actual price, discount, rating, and reviews — what should the discounted listing price be to stay competitive and maximize sales?"*

This project builds a Machine Learning model trained on **real Amazon India scraped data** to predict the optimal discounted listing price for any product.

---

## 🎯 Objective

| | |
|--|--|
| **Input** | actual_price, rating, rating_count, category, price_tier, log_rating_count, rating_power |
| **Output** | Predicted discounted listing price (₹) |
| **Models** | Multiple Linear Regression + Polynomial Regression (Degree 2) |
| **Dataset** | Real Amazon India scraped data — 1,465 products |

---

## 📊 Dataset

| Property | Value |
|----------|-------|
| Source | Real Amazon India scraped data (Kaggle 2023) |
| Raw rows | 1,465 |
| Raw columns | 16 |
| Features used for training | 7 |
| Target variable | `discounted_price` (₹) |
| Price range | ₹39 — ₹77,990 |
| Average discount across dataset | 47% |

---

## 🧹 Real-World Data Quality Issues Handled

| Column | Problem | Fix |
|--------|---------|-----|
| `discounted_price` | `₹` prefix + `,` separators (`₹1,099`) | `str.replace` + `pd.to_numeric` |
| `actual_price` | `₹` prefix + `,` separators | `str.replace` + `pd.to_numeric` |
| `discount_percentage` | `%` suffix (`64%`) | `str.replace` + `pd.to_numeric` |
| `rating` | Rogue `\|` value mixed with floats | `pd.to_numeric(errors='coerce')` |
| `rating_count` | Indian number format `1,79,691` + 2 NaN | Remove all `,` + fill NaN with median |
| `category` | Full pipe-chain `Computers&Accessories\|Cables\|USB` | Split on `\|` take first element |

---

## ⚠️ Data Leakage — Identified and Fixed

Two features mathematically reconstructed the target — causing fake R² = 1.0000:

```
savings_amount      = actual_price - discounted_price
                    → discounted_price = actual_price - savings_amount

discount_percentage = (actual - discounted) / actual × 100
                    → discounted_price = actual × (1 - discount_pct/100)
```

Both were identified and dropped before training. This is a critical step that most beginners miss.

---

## ⚙️ Feature Engineering

| Feature | Formula | Business Meaning |
|---------|---------|-----------------|
| `price_tier` | `pd.cut` → Budget/Mid/Premium/Luxury | Categorical price context for the model |
| `rating_power` | `rating × log_rating_count` | Combined trust and popularity signal |

---

## 🔢 Encoding

| Column | Method | Reason |
|--------|--------|--------|
| `category` | Target Guided Ordinal | Ranked by mean discounted_price |
| `price_tier` | Ordinal (1–4) | Natural order: Budget < Mid-Range < Premium < Luxury |

---

## 📈 Model Performance

### Multiple Linear Regression

| Metric | Value |
|--------|-------|
| MAE | ₹799.02 |
| MSE | 3,651,385.83 |
| RMSE | ₹1,910.86 |
| R² | 0.9221 |
| Adjusted R² | 0.9206 |

### Polynomial Regression (Degree 2)

| Metric | Value |
|--------|-------|
| MAE | ₹757.44 |
| MSE | 3,245,808.54 |
| RMSE | ₹1,801.61 |
| R² | 0.9308 |
| Adjusted R² | 0.9232 |

---

## 🔄 Cross Validation (5-Fold) — The Real Story

| | MLR | Polynomial |
|--|-----|-----------|
| CV RMSE per fold | 2076, 1954, 2050, 1887, 1615 | 1885, 2033, 2401, 1854, 1348 |
| CV RMSE mean | **₹1,917** | **₹1,904** |
| CV R² per fold | 0.9146, 0.9438, 0.8996, 0.9089, 0.9404 | 0.9296, 0.9391, 0.8622, 0.9121, 0.9584 |
| CV R² mean | **0.9214** | **0.9203** |
| Test RMSE | ₹1,910 | ₹1,801 |
| CV vs Test RMSE gap | ₹7 ✅ | ₹103 ✅ |

**Important finding:** Unlike the synthetic dataset where Polynomial CV R² = 1.0 on every fold (severe overfitting), on this **real dataset** both models show honest and consistent CV scores. Neither model is overfitting. This is what real data looks like.

---

## 🏆 Model Selection

```
Test metrics  → Polynomial wins (R² 0.9308 vs 0.9221)
CV metrics    → Both honest and consistent
Sample errors → MLR total ₹6,353 vs Polynomial ₹10,787 on 8 products
Final choice  → Polynomial by test metrics (no overfitting detected on real data)
```

---

## 📉 Sample Predictions — MLR vs Polynomial

### MLR
| Actual (₹) | Predicted (₹) | Error (₹) |
|------------|--------------|-----------|
| 26,999 | 23,006 | 3,993 |
| 199 | 192 | 7 |
| 399 | 255 | 144 |
| 299 | 126 | 173 |
| 999 | 946 | 53 |
| 1,399 | 1,611 | -212 |
| 1,799 | 2,849 | -1,050 |
| 2,799 | 2,078 | 721 |

**Total absolute error: ₹6,353**

### Polynomial
| Actual (₹) | Predicted (₹) | Error (₹) |
|------------|--------------|-----------|
| 26,999 | 18,354 | 8,645 |
| 199 | 268 | -69 |
| 399 | 689 | -290 |
| 299 | 460 | -161 |
| 999 | 1,182 | -183 |
| 1,399 | 1,490 | -91 |
| 1,799 | 2,034 | -235 |
| 2,799 | 1,686 | 1,113 |

**Total absolute error: ₹10,787**

**Observation:** MLR makes smaller total errors on individual products despite slightly lower overall R². The ₹26,999 laptop is the hardest product for both models — it sits far above the dataset average and lacks brand information (Apple vs local brand) which would be the strongest signal for that price range.

---

## 🔑 Feature Correlation with Target

| Feature | Correlation | Interpretation |
|---------|-------------|----------------|
| `actual_price` | 0.96 | Dominant predictor — MRP sets the price ceiling |
| `price_tier` | 0.61 | Luxury/Premium products command higher prices |
| `category` | 0.30 | Electronics > Home&Kitchen > Office |
| `rating` | 0.12 | Better rated products charge slightly more |
| `rating_power` | 0.10 | Combined trust signal adds marginal value |
| `log_rating_count` | 0.07 | Review count barely moves price alone |
| `rating_count` | -0.03 | Log transform captures this better |

**Key insight:** `actual_price` dominates at 0.96 correlation. The remaining 7% of variance unexplained is driven by brand name, product type, and sale events — information not available in this dataset.

---

## 🔧 Optimization Attempted — Log Transform on Y

**Hypothesis:** Log transforming Y would help because price range spans 136x (₹199 to ₹26,999).

**Result:**

| Metric | Original MLR | Log Transform MLR |
|--------|-------------|------------------|
| MAE | ₹799 | ₹1,024 ❌ |
| RMSE | ₹1,910 | ₹2,571 ❌ |
| R² | 0.9221 | 0.8589 ❌ |

**Why it failed:** `actual_price` correlates with `discounted_price` at 0.96 — the relationship is already linear, not multiplicative. Log transform broke that linearity and worsened all metrics. Reverted to original MLR.

**Lesson:** Log transform is industry standard for price data but the data always decides. Trying and honestly reporting failure is part of the data science process.

---

## 🧪 Live Price Prediction — Business Simulation

```
Input  : USB-C Cable
         actual_price  : ₹999
         discount      : 35%
         rating        : 4.2
         reviews       : 5,000
         category      : Computers&Accessories
         price_tier    : Mid-Range

Output :
══════════════════════════════════════════════════
   AMAZON PRICE PREDICTION ENGINE
══════════════════════════════════════════════════
   Actual Price         :      ₹999
   Discount             :       35%
   Manual Calc Price    :      ₹649   ← simple arithmetic
   MLR Predicted Price  :      ₹473   ← market-informed
   Poly Predicted Price :      ₹784   ← market-informed
══════════════════════════════════════════════════

Insight : Model recommends ₹473 vs manual ₹649 because it
          learned from 1,465 real products that cables in
          competitive mid-range categories sell at lower
          realized prices than their stated discounts suggest.
```

---

## 🗂️ Project Structure

```
amazon-price-prediction/
│
├── data/
│   └── amazon.csv                       ← real Amazon India dataset
│
├── notebooks/
│   └── Amazon_Price_Prediction.ipynb    ← full ML pipeline
│
└── README.md
```

---

## 🔧 Tech Stack

| Tool | Usage |
|------|-------|
| Python 3.10 | Core language |
| Pandas | Data cleaning and manipulation |
| NumPy | Feature engineering |
| Matplotlib / Seaborn | EDA and residual visualizations |
| Scikit-Learn | StandardScaler, LinearRegression, PolynomialFeatures, cross_val_score, metrics |

---

## 🚀 How to Run

```bash
# 1. Place both files in the same folder
#    amazon.csv
#    Amazon_Price_Prediction.ipynb

# 2. Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn jupyter

# 3. Launch Jupyter
jupyter notebook Amazon_Price_Prediction.ipynb

# 4. Kernel → Restart & Run All
```

---

## 📄 Resume Bullet Points

```
• Built an Amazon India Product Price Prediction Engine on real scraped data
  (1,465 products) using Multiple Linear Regression and Polynomial Regression

• Identified and fixed two data leakage paths where engineered features
  mathematically reconstructed the target — preventing fake R² = 1.0000

• Cleaned production-quality e-commerce data: ₹ symbols, Indian comma
  format (1,79,691), % suffixes, rogue non-numeric values, pipe-chain categories


• Validated models with 5-fold CV — MLR CV R² 0.9214, Polynomial CV R² 0.9203
  confirming genuine generalization on real data (no overfitting)

• Attempted log-transform optimization — honestly reported it worsened metrics
  (R² dropped 0.9221 → 0.8589) demonstrating data-driven decision making

• Final Polynomial model explains 93.1% of price variation with MAE ₹757
  across products ranging from ₹39 cables to ₹77,990 laptops
```

---

## 🔮 Future Improvements

| Improvement | Expected Impact |
|------------|----------------|
| Extract product type from name (Cable/Laptop/TV) | High — biggest missing signal |
| Add brand name as feature | High — Apple vs local brand = 10x price difference |
| Train separate model per category | Medium — Electronics and Home&Kitchen behave differently |
| Ridge Regression on polynomial features | Medium — regularization to reduce variance |
| Streamlit web app deployment | Portfolio — live demo for recruiters |
| Add sale season (Prime Day, Diwali) | Medium — seasonal pricing patterns |

---

## 💡 Key Learnings

```
1. Data leakage is subtle — features that seem useful can mathematically
   reconstruct the target and produce fake 100% accuracy

2. Cross validation reveals what test metrics hide — always validate
   CV scores against test scores before selecting a model

3. Optimization is not always improvement — log transform is industry
   standard for prices but worsened results here because the relationship
   was already linear. The data always decides.

4. Real data produces honest results — R² of 0.93 on real Amazon data
   is a genuine achievement. Synthetic data where the model reverses
   the generation formula is not real model performance.
```

---

*Dataset: Amazon India Sales Dataset — Kaggle (2023)*  
*Built for portfolio and learning purposes*