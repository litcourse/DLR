# PISA 2022 Raw Data Directory Placeholder

This folder is a placeholder for the raw PISA 2022 SPSS datasets required for replication. Because these files are very large (approx. 1.5 GB in total), they are not included directly in this git repository.

For the Chinese version of this guide, please see [README_zh.md](README_zh.md).

## Instructions

To execute the replication code successfully, you must place the raw data files here:

1.  **`CY08MSP_STU_QQQ.sav`** (Student questionnaire data)
2.  **`CY08MSP_SCH_QQQ.sav`** (School questionnaire data)

### Option A: Automatic Download (Recommended)
Simply run the downloader script from the repository root:
```bash
python scripts/download_data.py
```
This will automatically fetch, extract, and place both `.sav` files in this directory.

---

### Option B: Manual Download
If the script does not work, download them manually:
1.  Go to the official [OECD PISA 2022 Database](https://www.oecd.org/pisa/data/2022database/).
2.  Locate and download:
    *   **Student questionnaire data (SPSS™ format)** (`STU_QQQ_SPSS.zip`)
    *   **School questionnaire data (SPSS™ format)** (`SCH_QQQ_SPSS.zip`)
3.  Extract both zip files and move the extracted `.sav` files (`CY08MSP_STU_QQQ.sav` and `CY08MSP_SCH_QQQ.sav`) into this folder.
