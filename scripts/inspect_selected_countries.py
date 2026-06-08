import pandas as pd
import pyreadstat
import numpy as np

def main():
    stu_path = "data/CY08MSP_STU_QQQ.SAV"
    sch_path = "data/CY08MSP_SCH_QQQ.SAV"
    
    selected_cnts = ['USA', 'GBR', 'DEU', 'FRA', 'AUS', 'CAN', 'SGP', 'NZL', 'SWE', 'IRL']
    
    print("Reading selected columns and rows from student dataset...")
    # Read only specific columns and filter for selected countries
    cols_stu = ['CNT', 'CNTSCHID', 'CNTSTUID', 'ESCS', 'ST004D01T', 'GRADE', 'IMMIG', 'ICTRES', 'W_FSTUWT'] + [f'PV{i}MATH' for i in range(1, 11)]
    
    # We load student data
    df_stu, _ = pyreadstat.read_sav(stu_path, usecols=cols_stu)
    df_stu = df_stu[df_stu['CNT'].isin(selected_cnts)]
    
    print(f"Loaded student records for selected countries: {len(df_stu)}")
    
    # Read school data
    cols_sch = ['CNT', 'CNTSCHID', 'RATCMP1', 'DIGPREP', 'SC017Q09JA', 'SC017Q10JA']
    df_sch, _ = pyreadstat.read_sav(sch_path, usecols=cols_sch)
    df_sch = df_sch[df_sch['CNT'].isin(selected_cnts)]
    
    print(f"Loaded school records for selected countries: {len(df_sch)}")
    
    print("\nStudent Data Summary by Country:")
    for cnt in selected_cnts:
        sub = df_stu[df_stu['CNT'] == cnt]
        print(f"Country: {cnt}")
        print(f"  Total Students: {len(sub)}")
        print(f"  ESCS Missing: {sub['ESCS'].isnull().sum()} ({sub['ESCS'].isnull().mean()*100:.1f}%)")
        print(f"  ICTRES Missing: {sub['ICTRES'].isnull().sum()} ({sub['ICTRES'].isnull().mean()*100:.1f}%)")
        print(f"  PV1MATH Missing: {sub['PV1MATH'].isnull().sum()} ({sub['PV1MATH'].isnull().mean()*100:.1f}%)")
        
    print("\nSchool Data Summary by Country:")
    for cnt in selected_cnts:
        sub = df_sch[df_sch['CNT'] == cnt]
        print(f"Country: {cnt}")
        print(f"  Total Schools: {len(sub)}")
        print(f"  RATCMP1 Missing: {sub['RATCMP1'].isnull().sum()} ({sub['RATCMP1'].isnull().mean()*100:.1f}%)")
        print(f"  DIGPREP Missing: {sub['DIGPREP'].isnull().sum()} ({sub['DIGPREP'].isnull().mean()*100:.1f}%)")

if __name__ == "__main__":
    main()
