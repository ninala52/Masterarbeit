from FirmSample import FirmSample


class Main:
    @staticmethod
    def main():
        csv_path = r"C:\Users\PC\Downloads\Loughran-McDonald_10X_Summaries_1993-2024.csv"

        sample_builder = FirmSample(csv_path, start_year=2019, end_year=2023)
        df_one = sample_builder.build_sample()


        print("\nSample fertig gebaut. Zeilen df_one:", len(df_one))


if __name__ == "__main__":
    Main.main()
