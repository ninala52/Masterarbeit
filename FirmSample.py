import pandas as pd


class FirmSample:
    """
    Baut dein 10-K Firmensample nach den gewünschten Filtern
    und speichert Zwischenschritte als Attribute.
    """

    TENK_FORMS = {
        "10-K",
        "10-K405",
        "10KSB",
        "10-KSB",
        "10KSB40",
    }

    def __init__(self, csv_path: str, start_year: int = 2019, end_year: int = 2023):
        self.csv_path = csv_path
        self.start_year = start_year
        self.end_year = end_year

        self.df_raw = None
        self.df_non_fin_util = None
        self.df_one = None

    def build_sample(self) -> pd.DataFrame:
        """Führt alle Schritte aus und gibt das deduplizierte Sample (df_one) zurück."""
        self._read_data()
        self._add_year_column()
        self._filter_years()
        self._filter_form_types()
        self._convert_sic_to_numeric()
        self._exclude_financials_and_utilities()
        self._deduplicate_latest_filing()
        self._print_stats()
        return self.df_one

    # ------- Helper-Methoden -------

    def _read_data(self):
        self.df_raw = pd.read_csv(self.csv_path)

    def _add_year_column(self):
        self.df_raw["year"] = (self.df_raw["FILING_DATE"] // 10000).astype(int)

    def _filter_years(self):
        self.df_raw = self.df_raw[
            (self.df_raw["year"] >= self.start_year)
            & (self.df_raw["year"] <= self.end_year)
        ]

    def _filter_form_types(self):
        self.df_raw = self.df_raw[self.df_raw["FORM_TYPE"].isin(self.TENK_FORMS)]

    def _convert_sic_to_numeric(self):
        self.df_raw["SIC"] = pd.to_numeric(self.df_raw["SIC"], errors="coerce")

    def _exclude_financials_and_utilities(self):
        is_financial = (self.df_raw["SIC"] >= 6000) & (self.df_raw["SIC"] <= 6999)
        is_utility = (self.df_raw["SIC"] >= 4900) & (self.df_raw["SIC"] <= 4999)
        self.df_non_fin_util = self.df_raw[~(is_financial | is_utility)].copy()

    def _deduplicate_latest_filing(self):
        self.df_non_fin_util.loc[:, "FILING_DATE"] = pd.to_numeric(
            self.df_non_fin_util["FILING_DATE"], errors="coerce"
        )

        self.df_one = (
            self.df_non_fin_util
            .sort_values(["CIK", "year", "FILING_DATE"])
            .drop_duplicates(subset=["CIK", "year"], keep="last")
            .copy()
        )

    def _print_stats(self):
        print("VOR Dedup:")
        print("Anzahl 10-K-Filings:", len(self.df_non_fin_util))
        print("Anzahl unterschiedlicher Firmen (CIKs):", self.df_non_fin_util["CIK"].nunique())
        print("Anzahl Firm-Year-Observations:",
              len(self.df_non_fin_util[["CIK", "year"]].drop_duplicates()))

        dups_pre = (
            self.df_non_fin_util
            .groupby(["CIK", "year"])
            .size()
            .reset_index(name="n")
        )
        print("Anzahl (CIK, year) mit n>1 VOR Dedup:",
              len(dups_pre[dups_pre["n"] > 1]))

        print("\nNACH Dedup (pro CIK & Jahr nur aktuellstes Filing):")
        print("Anzahl 10-K-Filings:", len(self.df_one))
        print("Anzahl unterschiedlicher Firmen (CIKs):", self.df_one["CIK"].nunique())
        print("Anzahl Firm-Year-Observations:",
              len(self.df_one[["CIK", "year"]].drop_duplicates()))

        dups_after = (
            self.df_one
            .groupby(["CIK", "year"])
            .size()
            .reset_index(name="n")
        )
        print("Anzahl (CIK, year) mit n>1 NACH Dedup (sollte 0 sein):",
              len(dups_after[dups_after["n"] > 1]))

        # Filing-Jahr = Textjahr t, wir messen Performance in t+1
        self.df_one["perf_year"] = self.df_one["year"] + 1

        print("\nBeispiel-Zeilen (CIK, year, perf_year):")
        print(self.df_one[["CIK", "year", "perf_year"]].head())

        # Falls du später URLs bauen oder mit der SEC-Submissions-API arbeiten willst:
        self.df_one["CIK_str"] = self.df_one["CIK"].astype(int).astype(str).str.zfill(10)

        print("\nBeispiel CIK-Format (numerisch vs. String):")
        print(self.df_one[["CIK", "CIK_str"]].head())

        # --- Schritt 4: Panel abspeichern ---

        output_path = r"C:\Users\PC\Downloads\firm_year_10K_panel_2019_2023_nonfin_nonutil.csv"
        self.df_one.to_csv(output_path, index=False)
        print(f"\nPanel-Datei gespeichert unter: {output_path}")