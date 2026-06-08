import time
import requests

def test_speed():
    url = "https://zenodo.org/records/13382904/files/CY08MSP_SCH_QQQ.sav?download=1"
    print("Testing Zenodo download speed...")
    start_time = time.time()
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code != 200:
            print(f"Failed to connect to Zenodo, status code: {r.status_code}")
            return
        
        dl = 0
        total_length = int(r.headers.get('content-length', 0))
        print(f"Content-Length: {total_length / (1024*1024):.2f} MB")
        
        for chunk in r.iter_content(chunk_size=1024*1024):  # 1MB chunks
            if chunk:
                dl += len(chunk)
                elapsed = time.time() - start_time
                speed = dl / (1024 * 1024) / elapsed if elapsed > 0 else 0
                print(f"Downloaded {dl/(1024*1024):.2f} MB. Speed: {speed:.2f} MB/s")
                if dl > 5 * 1024 * 1024:  # test only 5MB
                    print("Test finished successfully!")
                    break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_speed()
