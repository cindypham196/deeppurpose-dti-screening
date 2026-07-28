import sys, os, io, re
import csv
import zlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from pathlib import Path
import argparse

# Point to your three CSVs
files = ["P23560.csv", "P59533.csv", "P30542.csv"]
#
#labels, values = [], []
#
#for f in files:
#    df = pd.read_csv(f)
#    if df.shape[1] < 4:
#        print(f"Skipping {f}: fewer than 4 columns.")
#        continue
#
#    # Column 4 (1-based) is iloc[:, 3]; take the *first valid* numeric value
#    col4 = pd.to_numeric(df.iloc[:, 3], errors="coerce")
#    col4_first = col4.dropna().iloc[0] if not col4.dropna().empty else None
#
#    if col4_first is None:
#        print(f"Skipping {f}: no numeric value in column 4.")
#        continue
#
#    labels.append(Path(f).stem)
#    values.append(col4_first)
#
## 2) Plot all three values in one chart
#plt.figure()
#plt.bar(labels, values)
#plt.ylabel("Binding score")
#plt.xlabel("Protein Targets")
#plt.title("Binding affinity of TOP 1 SMILE")
#plt.tight_layout()
#plt.show()
# ==============================

#--- choose which row to plot ---
ROW_INDEX = 5     # 0-based (0 = first row, 1 = second, ...)
NTH_VALID = None   # OR set to an integer (1-based) to take the nth non-NaN value; leave None to use ROW_INDEX

# --- CLI ---
labels, values = [], []

for f in files:
    df = pd.read_csv(f)
    if df.shape[1] < 4:
        print(f"Skipping {f}: fewer than 4 columns.")
        continue

    s = pd.to_numeric(df.iloc[:, -1], errors="coerce")  # last (4th) column as numeric

    if NTH_VALID is not None:
        non_na = s.dropna()
        if 1 <= NTH_VALID <= len(non_na):
            val = non_na.iloc[NTH_VALID - 1]
            row_desc = f"nth-valid={NTH_VALID}"
        else:
            print(f"Skipping {f}: fewer than {NTH_VALID} valid values in last column.")
            continue
    else:
        if 0 <= ROW_INDEX < len(s):
            val = s.iloc[ROW_INDEX]
            if pd.isna(val):
                print(f"Skipping {f}: value at row {ROW_INDEX} is NaN.")
                continue
            row_desc = f"row={ROW_INDEX}"
        else:
            print(f"Skipping {f}: --row {ROW_INDEX} out of range (0..{len(s)-1}).")
            continue

    labels.append(Path(f).stem)
    values.append(val)

if not values:
    raise SystemExit("No values to plot (all skipped).")

plt.figure()
plt.bar(labels, values)
plt.ylabel("Binding score")
plt.xlabel("Protein Targets")
plt.title(f"Binding scores of TOP {ROW_INDEX + 1} SMILE ")
plt.tight_layout()
plt.show()