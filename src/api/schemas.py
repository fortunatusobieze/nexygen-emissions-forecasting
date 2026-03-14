# Pydantic schemas (API contract)
from datetime import date
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, conint, confloat


# ---- Basic health ----
class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    detail: str = "Nexygen Emissions Forecast API is healthy."


# ---- Core forecast request/response ----
class ForecastRequest(BaseModel):
    scope: Literal["Scope 1", "Scope 2"] = Field(..., description="Emission scope")
    horizon_months: conint(gt=0, le=60) = Field(
        12, description="Number of months to forecast ahead (max 60)."
    )


class ForecastPoint(BaseModel):
    date: date
    scope: str
    forecast_emissions_tco2e: float
    target_emissions_tco2e: Optional[float] = None  
    gap_abs: Optional[float] = None                 
    gap_pct: Optional[float] = None                 

class ForecastResponse(BaseModel):
    scope: Literal["Scope 1", "Scope 2"]
    horizon_months: int
    points: List[ForecastPoint]


# ---- Scenario forecast ----
class ScenarioParameters(BaseModel):
    demand_growth_pct_per_year: confloat(ge=-50, le=50) = 0.0
    efficiency_improvement_pct_per_year: confloat(ge=0, le=50) = 0.0
    electricity_factor_reduction_pct_per_year: confloat(ge=0, le=50) = 0.0


class ScenarioForecastRequest(ForecastRequest):
    scenario_name: str = Field(..., description="User-friendly scenario label.")
    parameters: ScenarioParameters


class ScenarioForecastResponse(BaseModel):
    scenario_name: str
    scope: Literal["Scope 1", "Scope 2"]
    horizon_months: int
    points: List[ForecastPoint]


# ---- Targets / gap endpoint ----
class GapPoint(BaseModel):
    date: date
    scope: str
    actual_emissions_tco2e: float
    target_emissions_tco2e: Optional[float] = None 
    gap_abs: Optional[float] = None                 
    gap_pct: Optional[float] = None                 

class GapResponse(BaseModel):
    scope: Literal["Scope 1", "Scope 2"]
    points: List[GapPoint]
