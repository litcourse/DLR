import pyreadstat

def main():
    file_path = "data/CY08MSP_STU_QQQ.SAV"
    print("Reading CNT column from student dataset...")
    # Read only the CNT column
    df, metadata = pyreadstat.read_sav(file_path, usecols=['CNT'])
    
    print("\nTotal student records:", len(df))
    print("\nCountry counts (sorted alphabetically):")
    counts = df['CNT'].value_counts().sort_index()
    for cnt, count in counts.items():
        print(f"  {cnt}: {count}")
        
if __name__ == "__main__":
    main()
