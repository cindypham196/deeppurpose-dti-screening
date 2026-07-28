import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Load & clean each target file ----
def load_clean(path):
    """
    Reads a result CSV that may include commented headers (# ...).
    Returns DataFrame with: molecule (lowercased), score (float), rank (1 = best).
    """
    df = pd.read_csv(path, comment="#", header=None,
                     names=["pos","molecule","target","score"])
    df = df.dropna(how="all")
    df["molecule"] = df["molecule"].astype(str).str.strip().str.lower()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["molecule","score"]).reset_index(drop=True)
    df["rank"] = df["score"].rank(method="min", ascending=True).astype(int)
    return df[["molecule","score","rank"]]

paths = {
    "P23560": "P23560.csv",  # BDNF
    "P30542": "P30542.csv",  # ADORA1
    "P59533": "P59533.csv",  # TAS2R38
}

dfs = {k: load_clean(p) for k,p in paths.items()}

# ---- Merge per-target ranks ----
from functools import reduce
merged = reduce(
    lambda l,r: pd.merge(l, r, on="molecule", how="outer", suffixes=("", "_dup")),
    [
        dfs["P23560"].rename(columns={"score":"score_P23560","rank":"rank_P23560"}),
        dfs["P30542"].rename(columns={"score":"score_P30542","rank":"rank_P30542"}),
        dfs["P59533"].rename(columns={"score":"score_P59533","rank":"rank_P59533"}),
    ],
)

# ---- Strict top-25 intersection & consensus mean rank ----
N = 25
mask = (merged["rank_P23560"] <= N) & (merged["rank_P30542"] <= N) & (merged["rank_P59533"] <= N)
inter25 = merged.loc[mask].copy()
inter25["mean_rank"] = inter25[["rank_P23560","rank_P30542","rank_P59533"]].mean(axis=1)

# Optional: exclude non-consumer-friendly scaffolds
exclude_keywords = ["hexadrone","epistane","androst","19-norandrostene",
                    "dehydroepiandrosterone","dhea","cyproheptadine"]
inter25["exclude"] = inter25["molecule"].apply(lambda s: any(kw in s for kw in exclude_keywords))
table = inter25[~inter25["exclude"]].copy()

# ---- Final table (sorted) ----
table["Molecule"] = table["molecule"].str.title()
table = table[["Molecule","rank_P23560","rank_P30542","rank_P59533","mean_rank"]] \
            .sort_values("mean_rank").reset_index(drop=True)
table.to_csv("top25_intersection_prioritized.csv", index=False)

# ---- Plot consensus mean rank ----
plt.figure(figsize=(8,5))
plt.barh(table["Molecule"], table["mean_rank"])
plt.gca().invert_yaxis()
plt.xlabel("Consensus mean rank (lower = better)")
plt.title("Top-25 Intersection: Consensus Mean Rank Across BDNF, ADORA1, TAS2R38")
plt.tight_layout()
plt.savefig("top25_consensus_meanrank.png")
plt.show()