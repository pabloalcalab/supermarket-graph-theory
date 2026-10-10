"""Turns survey answers into monthly purchases and picks the two product groups to compare."""

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

# How many purchases per month each answer is worth (method from the Extended Essay).
PURCHASES_PER_MONTH = {
    "weekly": 4,
    "twice_a_month": 2,
    "monthly": 1,
    "every_2_months": 0.5,
    "every_3_months": 0.33,
    "every_4_months_or_less": 0.25,
    "never": 0,
}

# Products left out of the comparison even if their score would put them in.
EXCLUDED = {"Sugar": "it is on the same shelf as the salt"}


def load_survey() -> pd.DataFrame:
    """Share of respondents who chose each frequency, per product."""
    return pd.read_csv(DATA / "survey_frequencies.csv", index_col="product")


def monthly_purchases(survey: pd.DataFrame) -> pd.Series:
    """Average purchases per month per product: sum of share × purchases for each answer."""
    weights = pd.Series(PURCHASES_PER_MONTH)
    return (survey[weights.index] * weights).sum(axis=1).sort_values(ascending=False)


def pick_groups(score: pd.Series, n: int = 7) -> tuple[list[str], list[str]]:
    """The n most-bought and the n least-bought products, without the excluded ones."""
    valid = score.drop(index=list(EXCLUDED))
    return list(valid.index[:n]), list(valid.index[-n:][::-1])
