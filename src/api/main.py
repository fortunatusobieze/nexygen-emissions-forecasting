from datetime import date
from typing import List

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException

from .schemas import (
    HealthStatus,
    ForecastRequest,
    ForecastResponse,
    ForecastPoint,
    ScenarioForecastRequest,
    ScenarioForecastResponse,
    GapResponse,
    GapPoint,
)
from .utils import load_monthly_data, load_model, filter_scope_series

app = FastAPI(
    title="Nexygen Emissions Forecast API",
    version="0.1.0",
    description="API for Scope 1 & 2 emissions forecasts and net-zero gap analysis.",
)

# -------- Health endpoint --------
@app.get("/health", response_model=HealthStatus, tags=["system"])
def health_check():
    return HealthStatus(status="ok")


# -------- Baseline forecast --------
@app.post("/forecasts", response_model=ForecastResponse, tags=["forecasts"])
def get_forecast(req: ForecastRequest):
    monthly_df = load_monthly_data()
    series = filter_scope_series(monthly_df, req.scope)

    if series.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {req.scope}")

    model = load_model(req.scope)
    horizon = req.horizon_months

    # Generate forecast values
    forecast_values = model.forecast(steps=horizon)

    # Build date index
    last_date = series.index.max()
    forecast_index = pd.date_range(
        last_date + pd.offsets.MonthEnd(1),
        periods=horizon,
        freq="ME",
    )

    # Build response points — targets set to None for now (not in dataset yet)
    points: List[ForecastPoint] = []
    for d, val in zip(forecast_index, forecast_values):
        points.append(
            ForecastPoint(
                date=d.date(),
                scope=req.scope,
                forecast_emissions_tco2e=float(val),
                target_emissions_tco2e=None,
                gap_abs=None,
                gap_pct=None,
            )
        )

    return ForecastResponse(
        scope=req.scope,
        horizon_months=horizon,
        points=points,
    )


# -------- Scenario forecast --------
@app.post("/forecasts/scenario", response_model=ScenarioForecastResponse, tags=["forecasts"])
def get_scenario_forecast(req: ScenarioForecastRequest):
    # Reuse baseline forecast
    base_req = ForecastRequest(scope=req.scope, horizon_months=req.horizon_months)
    base_resp = get_forecast(base_req)

    years = np.array([i / 12 for i in range(req.horizon_months)])
    demand_factor = (1 + req.parameters.demand_growth_pct_per_year / 100.0) ** years
    efficiency_factor = (1 - req.parameters.efficiency_improvement_pct_per_year / 100.0) ** years

    adjusted_points: List[ForecastPoint] = []
    for i, p in enumerate(base_resp.points):
        base_val = p.forecast_emissions_tco2e
        adjusted_val = base_val * demand_factor[i] * efficiency_factor[i]

        adjusted_points.append(
            ForecastPoint(
                date=p.date,
                scope=p.scope,
                forecast_emissions_tco2e=float(adjusted_val),
                target_emissions_tco2e=None,
                gap_abs=None,
                gap_pct=None,
            )
        )

    return ScenarioForecastResponse(
        scenario_name=req.scenario_name,
        scope=req.scope,
        horizon_months=req.horizon_months,
        points=adjusted_points,
    )


# -------- Targets gap analysis --------
@app.get("/targets/gap", response_model=GapResponse, tags=["targets"])
def get_targets_gap(scope: str = "Scope 1"):
    if scope not in ["Scope 1", "Scope 2"]:
        raise HTTPException(status_code=400, detail="scope must be 'Scope 1' or 'Scope 2'")

    monthly_df = load_monthly_data()
    df_scope = monthly_df[monthly_df["Emission_Type"] == scope].copy()

    if df_scope.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {scope}")

    df_scope = df_scope.sort_values("Date")

    points = [
        GapPoint(
            date=row["Date"].date(),
            scope=scope,
            actual_emissions_tco2e=float(row["Emissions_tCO2e"]),
            target_emissions_tco2e=None,
            gap_abs=None,
            gap_pct=None,
        )
        for _, row in df_scope.iterrows()
    ]

    return GapResponse(scope=scope, points=points)
