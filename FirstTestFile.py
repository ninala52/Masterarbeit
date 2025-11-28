import pandas as pd


class FirstTestFile ()
# 1. Einlesen
df = pd.read_csv(r"C:\Users\PC\Downloads\Loughran-McDonald_10X_Summaries_1993-2024.csv")

# 2. Jahr aus Filing-Date ziehen
df["year"] = (df["FILING_DATE"] // 10000).astype(int)

# 3. Zeitraum 2019–2024 filtern
df = df[(df["year"] >= 2019) & (df["year"] <= 2023)]

# 4. 10-K-Formtypen definieren
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

# 7. Anzahl der 10-K-Filings im Sample
n_filings = len(df_non_fin_util)
print("Anzahl 10-K-Filings 2019–2024 (ohne Financials & Utilities):", n_filings)

# 8. Prüfen, ob es pro CIK & Jahr mehrere Filings gibt
dups = (
    df_non_fin_util
    .groupby(["CIK", "year"])
    .size()
    .reset_index(name="n")
)

mehrfach = dups[dups["n"] > 1]
print("\nKombinationen (CIK, Jahr) mit mehr als einem 10-K-Filing:")
print(mehrfach)

# 9. Anzahl unterschiedlicher Firmen und Firm-Year-Beobachtungen
n_firms = df_non_fin_util["CIK"].nunique()
firm_years = df_non_fin_util[["CIK", "year"]].drop_duplicates()
n_firm_years = len(firm_years)

print("\nAnzahl unterschiedlicher Firmen (CIKs):", n_firms)
print("Anzahl Firm-Year-Observations:", n_firm_years)

# dups enthält ja CIK, year, n
multi = dups[dups["n"] > 1][["CIK", "year"]].copy()
multi["next_year"] = multi["year"] + 1

# alle (CIK, year) Paare im Basisdatensatz
firm_years = df_non_fin_util[["CIK", "year"]].drop_duplicates()

# Check: gibt es für (CIK, year+1) einen Eintrag?
check_next = multi.merge(
    firm_years,
    left_on=["CIK", "next_year"],
    right_on=["CIK", "year"],
    how="left",
    suffixes=("", "_next")
)

# Zeilen, wo year_next nicht NA ist → Firma hat auch im Folgejahr ein Filing
hat_folgejahr = check_next[~check_next["year_next"].isna()]
print("Anzahl Firmen mit 2 Filings in Jahr t UND einem Filing in t+1:",
      len(hat_folgejahr))