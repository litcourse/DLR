import pandas as pd
import pyreadstat
import numpy as np

def explore():
    stu_path = "data/CY08MSP_STU_QQQ.SAV"
    sch_path = "data/CY08MSP_SCH_QQQ.SAV"
    
    print("Loading student metadata to check columns...")
    _, stu_meta = pyreadstat.read_sav(stu_path, metadataonly=True)
    stu_cols = stu_meta.column_names
    
    print("Loading school metadata to check columns...")
    _, sch_meta = pyreadstat.read_sav(sch_path, metadataonly=True)
    sch_cols = sch_meta.column_names
    
    # We will read a small chunk of data (e.g., 10000 rows) to check how variables look
    print("Reading a chunk of student data...")
    df_stu_chunk, _ = pyreadstat.read_sav(stu_path, row_limit=20000)
    print("Student chunk shape:", df_stu_chunk.shape)
    
    # Check what countries are in the chunk
    if 'CNT' in df_stu_chunk.columns:
        print("\nCountries in first 20000 rows:")
        print(df_stu_chunk['CNT'].value_counts())
        
    # Check variables of interest
    key_vars = [
        'CNT', 'CNTSCHID', 'CNTSTUID', 'ESCS', 'ST004D01T', 'GRADE', 'IMMIG',
        'PV1MATH', 'PV2MATH', 'PV3MATH', 'PV4MATH', 'PV5MATH',
        'PV6MATH', 'PV7MATH', 'PV8MATH', 'PV9MATH', 'PV10MATH',
        'ICTHOME', 'ICTSCH', 'ICTRES'
    ]
    
    print("\nChecking key variables presence in student dataset:")
    for v in key_vars:
        present = v in df_stu_chunk.columns
        print(f"  {v}: {'Yes' if present else 'NO'}")
        if present:
            non_null = df_stu_chunk[v].notnull().sum()
            print(f"    Non-null count in chunk: {non_null} / {len(df_stu_chunk)}")
            # Show summary stats
            if df_stu_chunk[v].dtype in [np.float64, np.int64]:
                print(f"    Mean: {df_stu_chunk[v].mean():.3f}, Min: {df_stu_chunk[v].min():.3f}, Max: {df_stu_chunk[v].max():.3f}")
            elif df_stu_chunk[v].dtype == object:
                print(f"    Unique values: {df_stu_chunk[v].unique()[:5]}")
                
    # Now check school dataset chunk
    print("\nReading a chunk of school data...")
    df_sch_chunk, _ = pyreadstat.read_sav(sch_path, row_limit=1000)
    print("School chunk shape:", df_sch_chunk.shape)
    
    sch_key_vars = [
        'CNT', 'CNTSCHID', 'RATCMP1', 'RATCMP2', 'RATTAB', 'DIGDVPOL', 'DIGPREP', 'SC017Q09JA', 'SC017Q10JA'
    ]
    print("\nChecking key variables presence in school dataset:")
    for v in sch_key_vars:
        present = v in df_sch_chunk.columns
        print(f"  {v}: {'Yes' if present else 'NO'}")
        if present:
            non_null = df_sch_chunk[v].notnull().sum()
            print(f"    Non-null count in chunk: {non_null} / {len(df_sch_chunk)}")
            if df_sch_chunk[v].dtype in [np.float64, np.int64]:
                print(f"    Mean: {df_sch_chunk[v].mean():.3f}, Min: {df_sch_chunk[v].min():.3f}, Max: {df_sch_chunk[v].max():.3f}")
                
if __name__ == "__main__":
    explore()
