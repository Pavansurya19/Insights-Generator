# analytics.py

import matplotlib.pyplot as plt


def detect_kpis(df):
    kpis = {}

    for col in df.columns:
        name = col.lower()

        if "sales" in name or "revenue" in name:
            kpis["Total Sales"] = df[col].sum()

        if "profit" in name:
            kpis["Total Profit"] = df[col].sum()

        if "cost" in name:
            kpis["Total Cost"] = df[col].sum()

        if "quantity" in name or "qty" in name:
            kpis["Total Quantity"] = df[col].sum()

    return kpis


def auto_charts(df):
    charts = []
    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols[:3]:
        fig, ax = plt.subplots()
        df[col].plot(kind="hist", ax=ax)
        ax.set_title(f"{col} Distribution")
        charts.append(fig)

    return charts