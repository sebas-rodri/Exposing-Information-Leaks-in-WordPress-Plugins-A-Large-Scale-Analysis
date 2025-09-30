import csv
import sys


if len(sys.argv) != 3:
    sys.stderr.write("Usage: get_slug.py <csv_file> <index>\n")
    sys.exit(1)
csv_file = sys.argv[1]
idx = int(sys.argv[2])
with open(csv_file, newline='', encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    rows = list(reader)

slug = rows[idx + 1][3]
print(slug)