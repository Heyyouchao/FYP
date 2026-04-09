import joblib

FEATURE_COLS = joblib.load("models/feature_columns.pkl")

print(len(FEATURE_COLS))
print(FEATURE_COLS)

from collections import defaultdict

groups = defaultdict(list)

for col in FEATURE_COLS:
    if col.startswith("R1"):
        groups["R1"].append(col)
    elif col.startswith("R2"):
        groups["R2"].append(col)
    elif col.startswith("R3"):
        groups["R3"].append(col)
    elif col.startswith("R4"):
        groups["R4"].append(col)
    else:
        groups["OTHER"].append(col)

for k, v in groups.items():
    print(f"\n{k} ({len(v)} features):")
    for c in v:
        print(" ", c)

for col in FEATURE_COLS:
    if "log" in col:
        print(col)

for col in FEATURE_COLS:
    if col.startswith("R") and ":" in col and "log" not in col:
        print(col)


with open("feature_list.txt", "w") as f:
    for col in FEATURE_COLS:
        f.write(col + "\n")