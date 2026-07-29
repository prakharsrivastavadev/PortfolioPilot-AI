import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "Date",
    "Asset",
    "Quantity",
    "Buy Price",
    "Current Price",
]


def load_data(uploaded_file):
    """
    Safely load and validate portfolio data.
    """

    if uploaded_file is None:
        raise ValueError("No CSV file uploaded.")

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Unable to read CSV: {e}")

    if df.empty:
        raise ValueError("Uploaded CSV is empty.")

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    df = df.copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    numeric_columns = [
        "Quantity",
        "Buy Price",
        "Current Price",
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    df["Asset"] = (
        df["Asset"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df = df.dropna(
        subset=[
            "Date",
            "Quantity",
            "Buy Price",
            "Current Price",
        ]
    )

    df["Quantity"] = df["Quantity"].clip(lower=0)

    df["Buy Price"] = df["Buy Price"].clip(lower=0)

    df["Current Price"] = df["Current Price"].clip(lower=0)

    df = df.reset_index(drop=True)

    return df


def calculate_summary(df):
    """
    Portfolio summary.
    """

    if df.empty:

        return {
            "Investment": 0.0,
            "Current Value": 0.0,
            "Profit": 0.0,
            "Return %": 0.0,
        }

    investment = float(
        (df["Quantity"] * df["Buy Price"]).sum()
    )

    current = float(
        (df["Quantity"] * df["Current Price"]).sum()
    )

    profit = current - investment

    roi = (
        (profit / investment) * 100
        if investment > 0
        else 0.0
    )

    return {
        "Investment": investment,
        "Current Value": current,
        "Profit": profit,
        "Return %": roi,
    }


def asset_summary(df):
    """
    Portfolio grouped by asset.
    """

    if df.empty:

        return pd.DataFrame(
            columns=[
                "Asset",
                "Investment",
                "Current Value",
            ]
        )

    temp = df.copy()

    temp["Investment"] = (
        temp["Quantity"]
        * temp["Buy Price"]
    )

    temp["Current Value"] = (
        temp["Quantity"]
        * temp["Current Price"]
    )

    return (
        temp.groupby(
            "Asset",
            as_index=False,
        )[
            [
                "Investment",
                "Current Value",
            ]
        ]
        .sum()
        .sort_values(
            "Current Value",
            ascending=False,
        )
    )


def search_assets(df, keyword):
    """
    Safe asset search.
    """

    if df.empty:

        return df

    if keyword is None:

        return df

    keyword = str(keyword).strip()

    if keyword == "":

        return df

    return df[
        df["Asset"]
        .str.contains(
            keyword,
            case=False,
            regex=False,
            na=False,
        )
                  ]
