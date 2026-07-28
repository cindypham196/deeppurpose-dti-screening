import sys, os, io, re
import csv
import zlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from pathlib import Path
import DeepPurpose
from DeepPurpose import oneliner # produce DTI score
from rdkit import Chem
import requests # retrieve target sequences from UniProt using requests function
from rdkit import RDLogger

# Silence RDKit warnings to avoid the "not removing hydrogen..." spam
RDLogger.DisableLog('rdApp.warning')

# Function helps retrieve target sequences from UniProt
def fetch_uniprot_fasta(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# =============================================================
# ------------- the main program ------------------------------
# =============================================================

# UniProt accessions are 6 or 10 chars before any "-N"; allow isoform suffix like "-2"
ACC_RE = re.compile(r"^[A-Z0-9]{6}(?:[A-Z0-9]{4})?(?:-\d+)?$")
MAX_BASE_LEN = 10  

# User input IDs
uid = input("Enter a UniProt ID (e.g., P59533): ").strip().upper()

if not uid:
    print("RE-INPUT: no ID entered.")
elif not ACC_RE.fullmatch(uid):
    print("INVALID ID. Please re-enter")
else:
    print(f"VALID: {uid}")

# Load provided CSV file
df = pd.read_csv('dsld_ingredients_with_smiles.csv')

# Remove empty SMILES strings from the CSV file 
df = df.dropna(subset=['Ingredient', 'SMILES'])

# Remove duplicate SMILES strings, only keep 1 version
df['SMILES'] = df['SMILES'].astype(str).str.strip().str.replace(" ", "", regex=False)
df = df.drop_duplicates(subset=['SMILES'], keep='first').reset_index(drop=True)

# Make sure SMILES strings are valid
smiles_list=[]
smiles_name=[]
for s, i in zip(df['SMILES'], df['Ingredient']):
    if Chem.MolFromSmiles(s) is not None:
        smiles_list.append(s)
        smiles_name.append(i)
print(f"Valid molecules screened: {len(smiles_list)}")

# Use UniProt IDs to retrieve protein FASTA sequences
fasta = fetch_uniprot_fasta(uid)

# FASTA name
header_id = fasta.splitlines()[0] # Split header
fasta_symbol = header_id.split('|')[2].split()[0] # Take the symbol
fasta_name = header_id.split('|')[2].split(' OS=', 1)[0] # Take the symbol + name

# FASTA seq to feed oneliner.repurpose()
fasta_seq = ''.join(line.strip() for line in fasta.splitlines() if line and not line.startswith('>')).upper()

oneliner.repurpose(    
    target=fasta_seq,               # FASTA sequence without header
    target_name=fasta_symbol,         # Name of the target
    X_repurpose=smiles_list,        # SMILES column from the provided csv
    drug_names=smiles_name,         # Ingredient column from the provided csv
    pretrained=True,                # Use pretrained models from DeepPurpose
)

# Save results for each target to a structured .csv file
in_path = './save_folder/results_aggregation/repurposing.txt'
out_path = f'{uid}.csv'
rows = []
with open(in_path, 'r', encoding='utf-8') as in_file:
    for line in in_file:
        s = line.strip()
        # Skip border/empty lines like +----...----+
        if not s or s.startswith('+'):
            continue
        # Keep only table rows containing pipes
        if '|' not in s:
            continue

        # Split on '|' and strip whitespace; drop empty cells from leading/trailing pipes
        parts = [col.strip() for col in s.split('|')]
        parts = [col for col in parts if col != '']
        if parts:
            rows.append(parts)

# Write CSV
with open(out_path, 'w', newline='', encoding='utf-8') as out_file:
    # Brief summary
    out_file.write(f"# UniProt_ID,{uid}\n")
    out_file.write(f"# Target_name,{fasta_name}\n")
    out_file.write(f"# Molecules_screened,{len(smiles_list)}\n")
    out_file.write(f"# Generated_at,{pd.Timestamp.now().isoformat(timespec='seconds')}\n")
    out_file.write("#\n")
    
    # Write result table
    writer = csv.writer(out_file)
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {out_path}")
 
# Rank or highlight the most promising molecules for further development
NAME_COL  = "Drug Name"    
SCORE_COL = "Binding Score"

df2 = pd.read_csv(f'{uid}.csv', comment="#", header=0)
plot_df2 = (
    df2[[NAME_COL, SCORE_COL]]
      .assign(**{SCORE_COL: pd.to_numeric(df2[SCORE_COL], errors="coerce")})
      .dropna()
      .sort_values(SCORE_COL, ascending=True)   # lower = better
      .head(20)
)

# Take the first 20 molecules that have the lowerst binding score
scores20 = pd.to_numeric(plot_df2[SCORE_COL], errors="coerce").dropna().head(20)

# Horizontal bars for readability with long names
plt.figure()
plt.barh(plot_df2[NAME_COL].astype(str), plot_df2[SCORE_COL])
plt.xlim(0, scores20.iloc[19] + 10)
plt.gca().invert_yaxis()
plt.xlabel("Binding score (lower = better)")
plt.title(f"Top 20 predicted binders for {uid}({fasta_symbol})")
plt.tight_layout()
plt.show()


