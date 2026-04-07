"""Découpage par pays : un pays est entièrement en entraînement ou entièrement en test."""

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


def group_test_split(df: pd.DataFrame, test_size: float, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Met de côté une part `test_size` des **pays** (pas des lignes)."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(splitter.split(df, groups=df["country"]))
    return df.iloc[train_idx].reset_index(drop=True), df.iloc[test_idx].reset_index(drop=True)
