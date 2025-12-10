import pandas as pd
import re
import os

# ----------------------------------------------------
# Paths
# ----------------------------------------------------
base = "/Users/sruthivisvanathan/Downloads"

file_path = f"{base}/proj1sheet.xlsx"
cpi_path = f"{base}/CPILFESL.csv"
cci_path = f"{base}/USACSCICP02STSAM.csv"

out_path_wide = f"{base}/result1.csv"
out_path_long = f"{base}/result1_long.csv"
out_path_merged = f"{base}/monthlysales_cpi_cci.csv"

# ----------------------------------------------------
# 1) EXTRACT NAICS 446 + 44812 across year sheets (wide)
# ----------------------------------------------------
# Read all sheets
sheets = pd.read_excel(file_path, sheet_name=None)

out = []

for sheet_name, df in sheets.items():
    # Keep only year sheets (1992-2025)
    if not re.fullmatch(r"(199[2-9]|200\d|201\d|202[0-5])", str(sheet_name).strip()):
        continue

    # Standardize column names
    df.columns = [str(c).strip() for c in df.columns]

    # Locate NAICS column by name heuristic
    naics_col = None
    for c in df.columns:
        key = str(c).lower().replace(" ", "")
        if key in {"naicscode", "naics_code", "naics"}:
            naics_col = c
            break

    # If not found, assume first column is NAICS
    if naics_col is None and len(df.columns) > 0:
        naics_col = df.columns[0]

    # Clean NAICS values to digit strings
    def clean_naics(x):
        if pd.isna(x):
            return ""
        s = str(x).strip()
        s = re.sub(r"[^0-9]", "", s)
        return s

    df["naics_clean"] = df[naics_col].apply(clean_naics)

    # Filter targets (exact matches)
    df_filtered = df[df["naics_clean"].isin({"446", "44812"})].copy()

    if not df_filtered.empty:
        df_filtered["sheet"] = str(sheet_name).strip()
        out.append(df_filtered)

# Combine safely
if out:
    result = pd.concat(out, ignore_index=True, sort=False)
else:
    result = pd.DataFrame()

print("CWD:", os.getcwd())
print("Wide output path:", out_path_wide)
print("Rows in wide result:", len(result))
print("Columns in wide result:", len(result.columns))

# Save wide extract
result.to_csv(out_path_wide, index=False)
print("Saved wide extract:", out_path_wide)

# ----------------------------------------------------
# 2) RESHAPE result1.csv -> long monthly rows
#    Convert "Jan. 2024" / "May 2024" columns to dates
#    matching FRED-style monthly date column
# ----------------------------------------------------
if result.empty:
    # Still write empty long + merged files for consistency
    pd.DataFrame().to_csv(out_path_long, index=False)
    pd.DataFrame().to_csv(out_path_merged, index=False)
    print("No matching NAICS rows found. Long and merged outputs are empty.")
    raise SystemExit

# Use the in-memory `result` (same as result1.csv)
retail = result.copy()
retail.columns = [c.strip() for c in retail.columns]

# Drop helper columns we don't want to carry forward
for col in ["naics_clean"]:
    if col in retail.columns:
        retail = retail.drop(columns=[col])

# Identify month columns like "Jan. 2024" or "May 2024"
month_pattern = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})$")

month_cols = [c for c in retail.columns if month_pattern.match(str(c))]
id_cols = [c for c in retail.columns if c not in month_cols]

# Melt wide -> long
long_df = retail.melt(
    id_vars=id_cols,
    value_vars=month_cols,
    var_name="month_label",
    value_name="sales"
)

# Parse month_label -> datetime
def label_to_date(x):
    x = str(x).replace(".", "").strip()  # "Jan. 2024" -> "Jan 2024"
    return pd.to_datetime(x, format="%b %Y", errors="coerce")

long_df["observation_date"] = long_df["month_label"].apply(label_to_date)

# Drop rows where date didn't parse
long_df = long_df.dropna(subset=["observation_date"])

# Normalize to first day of month
long_df["observation_date"] = long_df["observation_date"].dt.to_period("M").dt.to_timestamp()

# Clean sales values
long_df["sales"] = (
    long_df["sales"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.strip()
    .replace({"(S)": None, "nan": None, "": None})
)
long_df["sales"] = pd.to_numeric(long_df["sales"], errors="coerce")

# Keep only actual values
long_df = long_df.dropna(subset=["sales"])

# (Optional) Keep only the two NAICS codes using whichever NAICS column exists
# Prefer a likely original NAICS column if present.
possible_naics_cols = [c for c in long_df.columns if str(c).lower().replace(" ", "") in {"naicscode", "naics_code", "naics"}]
if possible_naics_cols:
    nc = possible_naics_cols[0]
    long_df[nc] = long_df[nc].astype(str).str.strip()
    # Keep header-level exact matches if your new format uses exactly "446" and "44812"
    long_df = long_df[long_df[nc].isin(["446", "44812"])]

# Save long retail
long_df.to_csv(out_path_long, index=False)
print("Saved long retail:", out_path_long)
print("Rows in long retail:", len(long_df))

# ----------------------------------------------------
# 3) MERGE CPI + CCI on observation_date
# ----------------------------------------------------
cpi = pd.read_csv(cpi_path)
cci = pd.read_csv(cci_path)

# Ensure dates are datetime
cpi["observation_date"] = pd.to_datetime(cpi["observation_date"], errors="coerce")
cci["observation_date"] = pd.to_datetime(cci["observation_date"], errors="coerce")

merged = (
    long_df
    .merge(cpi, on="observation_date", how="left")
    .merge(cci, on="observation_date", how="left")
)
# ----------------------------
# Final cleanup + ordering
# ----------------------------

# Drop columns if they exist
cols_to_drop = ["sheet", "TOTAL"]
merged = merged.drop(columns=[c for c in cols_to_drop if c in merged.columns])

# Ensure NAICS column name matches your file
# (looks like "NAICS  Code" in your output)
naics_col = "NAICS  Code"

# Create custom order: 446 first, then 44812
order_map = {"446": 0, "44812": 1}

merged[naics_col] = merged[naics_col].astype(str).str.strip()
merged["_naics_order"] = merged[naics_col].map(order_map)

# Sort by NAICS order, then by date
merged = merged.sort_values(
    by=["_naics_order", "observation_date"],
    ascending=[True, True]
).drop(columns=["_naics_order"])

# Save updated merged file
merged.to_csv(out_path_merged, index=False)
print("Saved cleaned + ordered merged file:", out_path_merged)

merged.to_csv(out_path_merged, index=False)
print("Saved merged CPI+CCI:", out_path_merged)
print("Rows in merged:", len(merged))
