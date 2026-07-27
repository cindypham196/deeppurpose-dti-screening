Multi-Target DTI Screening & Consensus Ranking Pipeline

An end-to-end Python pipeline developed to screen, evaluate, and prioritize candidate small molecules from a curated ingredient list (`dsld_ingredients_with_smiles.csv`) against consumer-relevant biological targets.


🎯 Project Goal:
The primary objective of this exercise is to leverage deep learning-based Drug-Target Interaction (DTI) models (via the DeepPurpose framework) to identify promising consumer product ingredients (e.g., related to mood, alertness, taste, or cognitive support). 

By predicting binding affinities between small molecules and chosen protein targets, the pipeline translates raw structural SMILES data into prioritized candidates. In DeepPurpose, lower predicted binding scores indicate stronger binding affinity and higher potential biological activity.

⚙️  How the Pipeline Solves the Challenge:

This pipeline addresses the full workflow—from raw data ingestion to stakeholder reporting—through four key stages:

1. Data Preprocessing & Input Quality Control:
- Automatically drops incomplete or missing entries.
- Strips whitespace and deduplicates SMILES strings.
- Uses RDKit (`Chem.MolFromSmiles`) to validate molecular structures, discarding malformed SMILES prior to model inference.

2. Automated Sequence Fetching & Model Inference:
- Dynamically retrieves standard FASTA protein sequences directly from the **UniProt REST API** using 6- or 10-character accession IDs (e.g., `P23560`, `P30542`, `P59533`).
- Runs DeepPurpose's pretrained `oneliner.repurpose()` model across valid candidate SMILES and stores structured result tables per target.

3. Multi-Target Consensus Ranking & Domain Filtering:
- Instead of prioritizing molecules based on a single target, the pipeline aggregates individual target scores and ranks candidates across all biological targets simultaneously.
- Identifies candidate molecules meeting a strict top-N threshold (e.g., top 25) across all targets.
- Computes a **Consensus Mean Rank** across targets to find balanced multi-target hits.
- Applies rule-based domain filtering to exclude non-consumer-friendly scaffolds (e.g., anabolic steroids, heavy synthetic hormones).

4. Stakeholder Visualization & Output Delivery:
- Generates formatted output CSV files containing metadata and individual binding metrics.
- Automatically produces publication-ready **Matplotlib** visualizations to clearly communicate top-ranked candidates to non-technical stakeholders.


🛠️ Stack (Requirement.txt):
- Language: Python 3.
- Cheminformatics & ML: RDKit, DeepPurpose, PyTorch
- Data Processing & Viz: Pandas, NumPy, Matplotlib
- API Integration: Requests (UniProt API) 

📁 Code Overview:
* molecular_screening.py
  - Primary pipeline entry point for single-target screening.
  - Prompts the user for a UniProt accession ID, validates the format, and fetches the target FASTA sequence via `fetch_uniprot_fasta()`. Cleans and validates the SMILES dataset with RDKit, executes DeepPurpose predictions, formats raw outputs into structured CSV files with metadata, and plots a horizontal bar chart of the top 25 candidate binders.

* mean_rank.py
  - Multi-target aggregation, consensus ranking, and safety filtering.
  - Ingests output screening CSVs across multiple protein targets (e.g., `P23560`, `P30542`, `P59533`). Computes per-target numerical ranks, filters for molecules appearing in the top 25 across all targets, calculates a cross-target **consensus mean rank**, excludes non-consumer-friendly scaffolds via keyword filtering, and exports both a prioritized CSV (`top25_intersection_prioritized.csv`) and a summary plot (`top25_consensus_meanrank.png`).

* plot.py
  - Comparative visualization tool for specific ranked candidates.
  - Reads multiple target result CSVs and extracts binding scores for specific rank positions (e.g., comparing the top binder or a specific row across targets) to produce comparative bar charts across biological targets.

* import_csv.py
  - Utility parser for raw DeepPurpose output text.
  - Converts raw tabular text outputs generated in DeepPurpose's aggregation folder (`repurposing.txt`) into clean, structured CSV files (`teste.csv`) by stripping ASCII borders and formatting columns.

 Input Data:`dsld_ingredients_with_smiles.csv` dataset contains ingredient names and SMILES strings used as the screening library.


 🚀 Quickstart Guide
