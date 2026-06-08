import os
import zipfile
from fast_download import download_parallel

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path} to {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction completed.")
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")

def main():
    dest_folder = "data"
    os.makedirs(dest_folder, exist_ok=True)
    
    # Use 32 threads for parallel chunk downloads
    url_stu = "https://webfs.oecd.org/pisa2022/STU_QQQ_SPSS.zip"
    out_stu = os.path.join(dest_folder, "STU_QQQ_SPSS.zip")
    success_stu = download_parallel(url_stu, out_stu, num_threads=32, chunk_size_mb=10)
    if success_stu:
        extract_zip(out_stu, dest_folder)
        
    url_sch = "https://webfs.oecd.org/pisa2022/SCH_QQQ_SPSS.zip"
    out_sch = os.path.join(dest_folder, "SCH_QQQ_SPSS.zip")
    success_sch = download_parallel(url_sch, out_sch, num_threads=16, chunk_size_mb=2)
    if success_sch:
        extract_zip(out_sch, dest_folder)

if __name__ == "__main__":
    main()
