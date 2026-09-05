import os
import sys
import time
import zipfile
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import requests

URL = "https://warwick.ac.uk/fac/cross_fac/tia/data/arch/books_set.zip"
EXPECTED_SIZE = 5275751113
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Data", "raw", "arch")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books_set.zip")
CHUNK_SIZE = 64 * 1024  # 64 KB
MAX_RETRIES = 50

def format_bytes(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TB"

def download_part(part_idx, start, end, progress, lock):
    part_len = end - start + 1
    part_file = os.path.join(OUTPUT_DIR, f"books_set.zip.part_{part_idx:02d}")
    
    current_size = os.path.getsize(part_file) if os.path.exists(part_file) else 0
    if current_size > part_len:
        os.remove(part_file)
        current_size = 0
        
    with lock:
        progress[part_idx] = current_size
        
    if current_size == part_len:
        return True
        
    retries = 0
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    while current_size < part_len and retries < MAX_RETRIES:
        range_start = start + current_size
        headers = {"Range": f"bytes={range_start}-{end}"}
        try:
            with session.get(URL, headers=headers, stream=True, timeout=25) as resp:
                if resp.status_code not in (200, 206):
                    retries += 1
                    time.sleep(2)
                    continue
                    
                with open(part_file, "ab" if current_size > 0 else "wb") as f:
                    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            current_size += len(chunk)
                            with lock:
                                progress[part_idx] = current_size
                            retries = 0
        except Exception:
            retries += 1
            time.sleep(2)
            if os.path.exists(part_file):
                current_size = os.path.getsize(part_file)
                with lock:
                    progress[part_idx] = current_size

    return current_size == part_len

def merge_parts(num_parts):
    print("\n[*] All parts downloaded! Merging into books_set.zip...", flush=True)
    merge_start = time.time()
    with open(OUTPUT_FILE, "wb") as outfile:
        for i in range(num_parts):
            part_file = os.path.join(OUTPUT_DIR, f"books_set.zip.part_{i:02d}")
            with open(part_file, "rb") as infile:
                while True:
                    buf = infile.read(4 * 1024 * 1024)
                    if not buf:
                        break
                    outfile.write(buf)
    print(f"[+] Merged successfully in {time.time() - merge_start:.1f} seconds.", flush=True)
    
    # Cleanup part files
    for i in range(num_parts):
        part_file = os.path.join(OUTPUT_DIR, f"books_set.zip.part_{i:02d}")
        try:
            os.remove(part_file)
        except OSError:
            pass

def verify_zip(filepath):
    print("[*] Verifying ZIP archive integrity...", flush=True)
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            bad_file = zf.testzip()
            if bad_file:
                print(f"[-] ZIP integrity check failed at: {bad_file}")
                return False
            namelist = zf.namelist()
            print(f"[+] ZIP integrity verified successfully! Total files: {len(namelist):,}")
            print("[*] Sample files inside ZIP:")
            for name in namelist[:5]:
                print(f"    - {name}")
            return True
    except Exception as err:
        print(f"[-] Error verifying ZIP: {err}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Multi-threaded downloader for ARCH books_set.zip")
    parser.add_argument("--parts", type=int, default=16, help="Number of parts to slice file into (default: 16)")
    parser.add_argument("--threads", type=int, default=10, help="Number of parallel worker threads (default: 10)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # If already completed
    if os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) == EXPECTED_SIZE:
        print(f"[+] {OUTPUT_FILE} is already fully downloaded ({format_bytes(EXPECTED_SIZE)}).")
        if verify_zip(OUTPUT_FILE):
            return 0
        else:
            print("[!] Existing file is corrupt. Removing and redownloading...")
            os.remove(OUTPUT_FILE)

    # Clean up any leftover single-stream partial file if present
    if os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) < EXPECTED_SIZE:
        os.remove(OUTPUT_FILE)

    print(f"[*] Starting multi-threaded download:")
    print(f"    Target:  {os.path.abspath(OUTPUT_FILE)}")
    print(f"    Size:    {format_bytes(EXPECTED_SIZE)} ({EXPECTED_SIZE:,} bytes)")
    print(f"    Slices:  {args.parts} parts (~{format_bytes(EXPECTED_SIZE / args.parts)} each)")
    print(f"    Threads: {args.threads} parallel connections")

    part_size = EXPECTED_SIZE // args.parts
    tasks = []
    for i in range(args.parts):
        start = i * part_size
        end = (start + part_size - 1) if i < args.parts - 1 else EXPECTED_SIZE - 1
        tasks.append((i, start, end))

    progress = {i: 0 for i in range(args.parts)}
    lock = threading.Lock()
    done_event = threading.Event()

    def monitor():
        start_time = time.time()
        last_time = start_time
        last_bytes = sum(progress.values())
        
        while not done_event.is_set():
            time.sleep(3.0)
            now = time.time()
            with lock:
                curr_bytes = sum(progress.values())
            
            elapsed = now - last_time
            delta = curr_bytes - last_bytes
            speed = delta / elapsed if elapsed > 0 else 0
            
            percent = (curr_bytes / EXPECTED_SIZE) * 100
            remaining = EXPECTED_SIZE - curr_bytes
            eta_secs = int(remaining / speed) if speed > 0 else 0
            eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_secs))
            
            active_parts = sum(1 for p, sz in progress.items() if sz < (tasks[p][2] - tasks[p][1] + 1))
            
            print(
                f"[{percent:5.1f}%] {format_bytes(curr_bytes)} / {format_bytes(EXPECTED_SIZE)} "
                f"| Speed: {format_bytes(speed)}/s | ETA: {eta_str} | Active parts: {active_parts}/{args.parts}",
                flush=True
            )
            last_time = now
            last_bytes = curr_bytes

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(download_part, idx, s, e, progress, lock): idx for idx, s, e in tasks}
        success = True
        for f in as_completed(futures):
            part_idx = futures[f]
            try:
                res = f.result()
                if not res:
                    print(f"[-] Part {part_idx} failed.", flush=True)
                    success = False
            except Exception as e:
                print(f"[-] Error in part {part_idx}: {e}", flush=True)
                success = False

    done_event.set()

    if not success or sum(progress.values()) != EXPECTED_SIZE:
        print("[-] Some parts failed to complete. You can rerun to resume missing parts.", flush=True)
        return 1

    merge_parts(args.parts)
    if verify_zip(OUTPUT_FILE):
        print("\n[+] Dataset ARCH books_set.zip downloaded and verified successfully!")
        return 0
    else:
        print("[-] ZIP validation failed after merge.", flush=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
