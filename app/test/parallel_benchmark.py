import sys
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

SCRIPTS = [
    "playwright_crawl.py",
    "selenium_crawl.py",
    "scrapy_crawl.py",
    "beautifulsoup_crawl.py"
]

def run_script(script, url):
    print(f"\nRunning {script} ...")
    result = subprocess.run(
        [sys.executable, script, url],
        cwd=".",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"Errors from {script}:\n{result.stderr}")

if __name__ == "__main__":
    url = sys.argv[1]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_script, f"app/test/{script}", url) for script in SCRIPTS]
        for f in futures:
            f.result()
