import os
import requests
import zipfile

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        
    filename = url.split('/')[-1]
    filepath = os.path.join(dest_folder, filename)
    
    print(f"Checking {url} ...")
    try:
        response = requests.head(url, allow_redirects=True, timeout=30)
    except Exception as e:
        print(f"Error checking HEAD for {url}: {e}")
        return None
        
    if response.status_code != 200:
        print(f"Error: URL {url} returned status code {response.status_code}")
        return None
        
    size_mb = int(response.headers.get('content-length', 0)) / (1024 * 1024)
    print(f"Found file. Size: {size_mb:.2f} MB")
    
    if os.path.exists(filepath):
        local_size = os.path.getsize(filepath)
        if abs(local_size - int(response.headers.get('content-length', 0))) < 1024:
            print(f"File {filename} already downloaded and matches size. Skipping download.")
            return filepath
            
    print(f"Downloading {filename} to {filepath}...")
    
    # Download with progress
    r = requests.get(url, stream=True, timeout=60)
    with open(filepath, 'wb') as f:
        dl = 0
        total_length = int(r.headers.get('content-length', 0))
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                dl += len(chunk)
                if total_length:
                    done = int(50 * dl / total_length)
                    print(f"\rProgress: [{'=' * done}{' ' * (50-done)}] {dl/(1024*1024):.2f}/{total_length/(1024*1024):.2f} MB", end='')
        print()
    print(f"Downloaded {filename} successfully.")
    return filepath

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
    urls = [
        "https://webfs.oecd.org/pisa2022/STU_QQQ_SPSS.zip",
        "https://webfs.oecd.org/pisa2022/SCH_QQQ_SPSS.zip"
    ]
    
    for url in urls:
        path = download_file(url, dest_folder)
        if path:
            extract_zip(path, dest_folder)

if __name__ == "__main__":
    main()
