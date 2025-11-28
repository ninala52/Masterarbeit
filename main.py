import pandas as pd

# 1. Einlesen
df = pd.read_csv(r"C:\Users\PC\Downloads\Loughran-McDonald_10X_Summaries_1993-2024.csv")

# 2. Jahr aus Filing-Date ziehen
df["year"] = (df["FILING_DATE"] // 10000).astype(int)

# 3. Zeitraum 2019–2023 filtern (anpassen, falls du 2024 willst)
df = df[(df["year"] >= 2019) & (df["year"] <= 2023)]

# 4. 10-K-Formtypen definieren (pure 10-Ks à la Hoberg & Phillips)
tenk_forms = {
    "10-K",
    "10-K405",
    "10KSB",
    "10-KSB",
    "10KSB40",
}
df = df[df["FORM_TYPE"].isin(tenk_forms)]

# 5. SIC als Zahl
df["SIC"] = pd.to_numeric(df["SIC"], errors="coerce")

# 6. Financials (6000–6999) und Utilities (4900–4999) ausschließen
is_financial = (df["SIC"] >= 6000) & (df["SIC"] <= 6999)
is_utility   = (df["SIC"] >= 4900) & (df["SIC"] <= 4999)
df_non_fin_util = df[~(is_financial | is_utility)]

# --- TEIL A: Status VOR Dedup ---

print("VOR Dedup:")
print("Anzahl 10-K-Filings:", len(df_non_fin_util))
print("Anzahl unterschiedlicher Firmen (CIKs):", df_non_fin_util["CIK"].nunique())
print("Anzahl Firm-Year-Observations:", len(df_non_fin_util[["CIK", "year"]].drop_duplicates()))

dups_pre = (
    df_non_fin_util
    .groupby(["CIK", "year"])
    .size()
    .reset_index(name="n")
)
print("Anzahl (CIK, year) mit n>1 VOR Dedup:", len(dups_pre[dups_pre["n"] > 1]))

# --- TEIL B: Dedup – pro CIK & Jahr das aktuellste Filing behalten ---

# FILING_DATE als Zahl (YYYYMMDD) sicherstellen
df_non_fin_util["FILING_DATE"] = pd.to_numeric(df_non_fin_util["FILING_DATE"], errors="coerce")

df_one = (
    df_non_fin_util
    .sort_values(["CIK", "year", "FILING_DATE"])
    .drop_duplicates(subset=["CIK", "year"], keep="last")
)

# --- TEIL C: Status NACH Dedup ---

print("\nNACH Dedup (pro CIK & Jahr nur aktuellstes Filing):")
print("Anzahl 10-K-Filings:", len(df_one))
print("Anzahl unterschiedlicher Firmen (CIKs):", df_one["CIK"].nunique())
print("Anzahl Firm-Year-Observations:", len(df_one[["CIK", "year"]].drop_duplicates()))

dups_after = (
    df_one
    .groupby(["CIK", "year"])
    .size()
    .reset_index(name="n")
)
print("Anzahl (CIK, year) mit n>1 NACH Dedup (sollte 0 sein):",
      len(dups_after[dups_after["n"] > 1]))