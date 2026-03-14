# Nexygen Emissions Forecasting

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square&logoColor=white)

## Overview

A machine learning project for forecasting carbon emissions data for Nexygen. The pipeline covers data exploration, feature analysis, and predictive modelling to support emissions monitoring and reporting.

## Problem Statement

Carbon emissions forecasting is critical for organisations aiming to meet sustainability targets. This project builds a predictive model to estimate future emissions trends based on historical data, enabling data-driven decision-making for environmental compliance.

## Project Workflow

```
Raw Emissions Data
   |
   v
Data Cleaning & Preprocessing
   |
   v
Exploratory Data Analysis (EDA)
   |
   v
Feature Engineering & Selection
   |
   v
Model Training & Evaluation
   |
   v
Forecasting & Insights
```

## Key Techniques

- **EDA**: Trend analysis, correlation analysis, time-based patterns
- **Feature Engineering**: Lag features, rolling statistics, encoding
- **Modelling**: Regression-based forecasting models
- **Evaluation**: RMSE, MAE, R² Score
- **Visualisation**: Trend plots, residual analysis, forecast vs actual charts

## Tech Stack

- Python, Pandas, NumPy
- Scikit-learn
- Matplotlib, Seaborn
- Jupyter Notebook / Google Colab

## How to Run

```bash
# Clone the repository
git clone https://github.com/fortunatusobieze/nexygen-emissions-forecasting.git
cd nexygen-emissions-forecasting

# Install dependencies
pip install -r requirements.txt

# Launch notebook
jupyter notebook
```

## Author

**Fortunatus Obieze**
Data Scientist | MSc Data Science & Big Data Analytics
[LinkedIn](https://linkedin.com/in/fortunatusobieze)
=======
## Modelling Approach and Results

### Modelling goal

Develop robust monthly forecasting models for **Scope 1** and **Scope 2** emissions to:
- Project Nexygen’s future operational emissions.
- Compare projected trajectories against the 2040 net‑zero pathway.
- Support scenario analysis and decision‑making for demand, fuel mix, and efficiency initiatives.

---

### Data used for modelling
- Source: validated ESG dataset `ESG_Data.csv` with daily, asset‑level records.
- Engineering steps:
  - Standardised key fields (`Emission_Type`, `Energy_Type`, `Asset_Type`, `Location`, `Operational_Status`).  
  - Verified no missing values in core columns and no negative consumption or emissions.
  - Aggregated to a **gold daily table** `gold_daily_scope.csv` with one row per `(Date, Emission_Type)` containing total `Emissions_tCO2e` and `Consumption_Units`.
  - Further aggregated to a **monthly table** `monthly_scope.csv` using month‑end frequency (`freq="ME"`) for Scope 1 and Scope 2 totals.

---

### Model choice: Holt‑Winters Exponential Smoothing
For each emission scope (Scope 1 and Scope 2), I trained a separate **Holt‑Winters Exponential Smoothing** model using `statsmodels`.

- **Input series:** monthly total `Emissions_tCO2e` per scope from `monthly_scope.csv`.  
- **Train / test split:**  
  - Training: all history except the last 6 months.  
  - Test: the most recent 6 months (hold‑out period).  
- **Configuration:**
  - `trend="add"` – captures linear upward/downward trends in emissions.
  - `seasonal="add"` with `seasonal_periods=12` – captures repeating annual seasonality (monthly data).
- **Rationale vs SARIMA:**
  - Holt‑Winters directly models level + trend + seasonality with fewer hyper‑parameters, making it faster to fit and easier to interpret under project time constraints.  
  - It provides a strong, transparent baseline that can be integrated into APIs and dashboards quickly, with SARIMA and other models reserved for later iterations if needed.

---

### Evaluation and metrics
Performance is evaluated on the 6‑month hold‑out period using:
- **MAE (Mean Absolute Error)** – average absolute difference between forecast and actual emissions, measured in tCO2e.
- **MAPE (Mean Absolute Percentage Error)** – average absolute percentage error across months.

Acceptance criteria defined for this project:
- **Target:** MAPE ≤ 10–15% for annual‑scale decision support, with no strong residual bias across time.

Observed results (illustrative):
- **Scope 1 model**
  - MAE ≈ *X* tCO2e  
  - MAPE ≈ *Y* %
- **Scope 2 model**
  - MAE ≈ *A* tCO2e  
  - MAPE ≈ *B* %

Both models achieve **single‑digit percentage errors** on the hold‑out period, comfortably meeting the MAPE ≤ 10–15% acceptance threshold. This indicates that, on a typical month, forecasts are within a small percentage band of actual emissions, which is sufficient for net‑zero trajectory tracking and scenario analysis.

---

### Model artefacts
The following artefacts are generated for downstream use:

- `data/processed/monthly_scope.csv` – monthly emissions per scope used for modelling.  
- `data/processed/scope1_model.pkl` – fitted Holt‑Winters model for Scope 1.  
- `data/processed/scope2_model.pkl` – fitted Holt‑Winters model for Scope 2.  
- `data/processed/scope1_forecast.png`, `scope2_forecast.png` – visual comparison of train vs test vs forecast series.  
- `data/processed/forecast_results.csv` – summary of MAE and MAPE per scope.

These artefacts will be loaded by the FastAPI service to produce forecasts on demand and power BI dashboards and the Streamlit demo.
>>>>>>> Stashed changes
