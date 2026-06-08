import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_chunk(url, start, end, chunk_num, temp_dir):
    chunk_path = os.path.join(temp_dir, f"chunk_{chunk_num}")
    headers = {"Range": f"bytes={start}-{end}"}
    
    # Retry logic
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=30)
            if r.status_code in [200, 206]:
                with open(chunk_path, "wb") as f:
                    for data in r.iter_content(chunk_size=8192):
                        f.write(data)
                return chunk_path, start, end
        except Exception as e:
            print(f"\nChunk {chunk_num} attempt {attempt+1} failed: {e}")
            time.sleep(2)
    raise Exception(f"Failed to download chunk {chunk_num}")

def download_parallel(url, output_path, num_threads=16, chunk_size_mb=10):
    print(f"Starting parallel download for {url} to {output_path}")
    
    # Get file size
    r = requests.head(url, allow_redirects=True, timeout=30)
    if r.status_code != 200:
        print(f"Error checking headers: {r.status_code}")
        return False
        
    accept_ranges = r.headers.get("Accept-Ranges", "")
    content_length = int(r.headers.get("Content-Length", 0))
    
    if not content_length:
        print("Content length is zero or missing.")
        return False
        
    print(f"File size: {content_length / (1024*1024):.2f} MB")
    
    # If range requests not supported, download normally
    if "bytes" not in accept_ranges.lower():
        print("Server does not support range requests. Downloading in single thread...")
        r = requests.get(url, stream=True, timeout=60)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True

    # Calculate chunks
    chunk_size = chunk_size_mb * 1024 * 1024
    chunks = []
    start = 0
    while start < content_length:
        end = min(start + chunk_size - 1, content_length - 1)
        chunks.append((start, end))
        start += chunk_size
        
    print(f"Dividing into {len(chunks)} chunks of {chunk_size_mb} MB each using {num_threads} threads")
    
    temp_dir = output_path + "_temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    completed_chunks = 0
    total_chunks = len(chunks)
    
    start_time = time.time()
    
    futures_map = {}
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for idx, (start_byte, end_byte) in enumerate(chunks):
            # Check if chunk already exists and matches expected size (resume capability)
            chunk_file = os.path.join(temp_dir, f"chunk_{idx}")
            expected_size = end_byte - start_byte + 1
            if os.path.exists(chunk_file) and os.path.getsize(chunk_file) == expected_size:
                completed_chunks += 1
                continue
                
            future = executor.submit(download_chunk, url, start_byte, end_byte, idx, temp_dir)
            futures_map[future] = idx
            
        if completed_chunks > 0:
            print(f"Found {completed_chunks}/{total_chunks} cached chunks. Resuming...")
            
        for future in as_completed(futures_map):
            idx = futures_map[future]
            try:
                future.result()
                completed_chunks += 1
                elapsed = time.time() - start_time
                percent = (completed_chunks / total_chunks) * 100
                speed = (completed_chunks * chunk_size_mb) / elapsed if elapsed > 0 else 0
                print(f"\rProgress: {completed_chunks}/{total_chunks} chunks ({percent:.1f}%) | Speed: {speed:.2f} MB/s", end="", flush=True)
            except Exception as e:
                print(f"\nError in chunk {idx}: {e}")
                # Clean up and exit
                return False
                
    print(f"\nAll chunks downloaded. Merging into {output_path}...")
    with open(output_path, "wb") as outfile:
        for idx in range(total_chunks):
            chunk_file = os.path.join(temp_dir, f"chunk_{idx}")
            with open(chunk_file, "rb") as infile:
                outfile.write(infile.read())
            os.remove(chunk_file)
            
    try:
        os.rmdir(temp_dir)
    except Exception:
        pass
        
    print(f"Download and merge complete. File saved to {output_path}.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fast_download.py <url> <output_path> [num_threads]")
        sys.exit(1)
        
    url = sys.argv[1]
    output = sys.argv[2]
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    
    download_parallel(url, output, num_threads=threads)
