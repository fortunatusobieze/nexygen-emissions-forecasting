#Utility functions
from pathlib import Path
from typing import Literal, Tuple

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"

SCOPE_MODELS = {
    "Scope 1": DATA_DIR / "scope1_model.pkl",
    "Scope 2": DATA_DIR / "scope2_model.pkl",
}

MONTHLY_PATH = DATA_DIR / "monthly_scope.csv"


def load_monthly_data() -> pd.DataFrame:
    df = pd.read_csv(MONTHLY_PATH, parse_dates=["Date"])
    return df


def load_model(scope: Literal["Scope 1", "Scope 2"]):
    path = SCOPE_MODELS[scope]
    model = joblib.load(path)
    return model


def filter_scope_series(monthly_df: pd.DataFrame, scope: str) -> pd.Series:
    series = (
        monthly_df[monthly_df["Emission_Type"] == scope]
        .set_index("Date")["Emissions_tCO2e"]
        .sort_index()
    )
    return series

from src.config import get_settings

settings = get_settings()
MODEL_DIR = Path(settings.model_dir)
DATA_DIR = Path(settings.data_dir)

