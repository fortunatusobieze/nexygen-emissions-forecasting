### 1. Emissions boundaries and forecasting requirements

**Scope definitions**  
  **Scope 1**: Direct GHG emissions from owned or controlled sources (e.g. on‑site fuel combustion, company fleet). 
  **Scope 2**: Indirect GHG emissions from the generation of purchased electricity, heat, or steam consumed by Nexygen assets 
  Emissions are expressed in **tCO2e** (metric tonnes of CO₂‑equivalent) in the field `Emissions_tCO2e`

  **Reporting boundary**  
  Daily, asset‑level records across Nexygen’s UK asset base (ServiceHub, Depot, Office, DataCentre, ControlRoom) with associated location and operational status.

  **Forecast horizon and refresh**  
  - Working forecasting grain: **monthly** total emissions per scope (aggregated from daily data).  
  - Planning horizon: forecasts out to **2040**, aligned with the net‑zero commitment and annual target pathway.  
  - Practical refresh cadence: models can be retrained or updated on a **monthly** basis as new data arrives.

 **Targets and “gap to target” logic**  
  The dataset includes annual net‑zero pathway fields:  
    `Target_Emissions_tCO2e` – annual emissions milestone for the net‑zero trajectory.[file:45]  
    `Reduction_Percentage_vs_BaseYear` – cumulative reduction vs 2020 baseline.[file:45]  
  For each forecast period, we define:  
    Absolute gap:  
      \[
      \text{gap\_abs} = \text{forecast\_emissions\_tCO2e} - \text{Target\_Emissions\_tCO2e}
      \]  
    Percentage gap:  
      \[
      \text{gap\_pct} = \frac{\text{gap\_abs}}{\text{Target\_Emissions\_tCO2e}}
      \]

  **Initial model acceptance criteria (to refine later)**  
  Train on historical period (e.g. 2020–2024), validate on hold‑out year (e.g. 2025).  
  Quantitative targets (for annual totals per scope):  
    - Mean Absolute Percentage Error (MAPE) ≤ 10–15% on validation.
  Qualitative checks:  
    - Residuals show no strong trend or systematic bias across time.  
    - Forecasts behave reasonably under scenario stress tests (no unrealistic spikes or negative emissions).


### 2. Dataset inventory and analytical structure

All core entities are currently represented in a single analytical table: `ESG_Data.csv`.

#### 2.1 Logical objects and mapping
| Logical object     | Columns in ESG_Data.csv                                                                                          |
|--------------------|-------------------------------------------------------------------------------------------------------------------|
| Emissions_Fact     | `Date`, `Year`, `Asset_ID`, `Emission_Type`, `Emissions_tCO2e`                                                   |
| Energy_Consumption | `Energy_Type`, `Consumption_Units`                                                                               |
| Asset_Dimension    | `Asset_ID`, `Asset_Type`, `Location`, `Operational_Status`                                                       |
| Targets_Table      | `Year`, `Target_Emissions_tCO2e`, `Reduction_Percentage_vs_BaseYear`  

> Note: Emission factors are implicitly embedded in `Emissions_tCO2e` (already calculated) rather than stored as a separate table in this version of the dataset.

#### 2.2 Data dictionary (current state)
| Column name                       | Type     | Description                                                                                         |
|----------------------------------|----------|-----------------------------------------------------------------------------------------------------|
| Date                             | datetime | Daily date of the measurement                                                                      |
| Year                             | int      | Calendar year corresponding to `Date`                                                              |
| Asset_ID                         | string   | Unique asset identifier (e.g. A001–A018)                                                           |
| Asset_Type                       | category | Asset category: ServiceHub, Depot, Office, DataCentre, ControlRoom                                  |
| Location                         | category | Geographic location: England, Scotland, Wales                                                      |
| Operational_Status               | category | Operational status of asset: Active, Paused, Decommissioned                                        |
| Energy_Type                      | category | Energy carrier: typically ELECTRICITY_KWH, GAS_KWH, DIESEL_L                                       |
| Consumption_Units                | float    | Energy consumed in units of `Energy_Type`                                                          |
| Emission_Type                    | category | Scope classification for the row: Scope 1 (direct) or Scope 2 (indirect purchased electricity)[file:45] |
| Emissions_tCO2e                  | float    | Emissions for that row in tonnes CO2‑equivalent                                                    |
| Target_Emissions_tCO2e           | float    | Annual emissions target (net‑zero pathway) associated with the row’s year                          |
| Reduction_Percentage_vs_BaseYear | float    | Percentage reduction vs 2020 base‑year emissions                                                   |

---


### 3. Data quality rules and completeness thresholds

The following rules define minimum data quality expectations for analysis and modelling:
**Non‑null requirements**  
  - No missing values allowed in: `Date`, `Year`, `Asset_ID`, `Asset_Type`, `Location`, `Energy_Type`, `Emission_Type`, `Emissions_tCO2e`.  
  - Overall completeness threshold: ≥ 95–99% non‑null coverage for `Consumption_Units` and `Target_Emissions_tCO2e`.

**Consistency checks**  
  - `Year` must equal `Date.year` for every row.  
  - `Consumption_Units ≥ 0` and `Emissions_tCO2e ≥ 0` (no negative consumption or emissions).  
  - `Emission_Type ∈ {"Scope 1", "Scope 2"}` (case and spelling standardised).  
  - `Energy_Type` restricted to known valid codes: `ELECTRICITY_KWH`, `GAS_KWH`, `DIESEL_L` (extend list if additional carriers exist).  
  - `Operational_Status` restricted to defined statuses, with the expectation that most forecast‑relevant assets are `Active`.

**Granularity (“grain”)**  
  - Base grain for `ESG_Data.csv`: **daily × asset × energy type × emission type**.  
  - Forecasting grain: monthly totals per emission scope, with optional breakdowns by asset type or region.
