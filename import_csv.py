import csv
import zlib

in_path = './save_folder/results_aggregation/repurposing.txt'
out_path = 'teste.csv'

rows = []
with open(in_path, 'r', encoding='utf-8') as in_file:
    for line in in_file:
        s = line.strip()
        # skip border/empty lines like +----...----+
        if not s or s.startswith('+'):
            continue
        # keep only table rows containing pipes
        if '|' not in s:
            continue

        # split on '|' and strip whitespace; drop empty cells from leading/trailing pipes
        parts = [col.strip() for col in s.split('|')]
        parts = [col for col in parts if col != '']
        if parts:
            rows.append(parts)

# write CSV
with open(out_path, 'w', newline='', encoding='utf-8') as out_file:
    writer = csv.writer(out_file)
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {out_path}")