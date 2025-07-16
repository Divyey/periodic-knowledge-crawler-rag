import schedule
import time
import subprocess

# ✅ Set your target product URL
URL = "https://preprod-arunodayakurtis.zupain.com/SILKKURTA(BLUE-)/pd/01f1b486-c0b1-409d-a016-12d1fd5adf2e"

def job():
    print("[Scheduler] Running crawl/upsert for target page...")
    subprocess.run([
        "python",
        "app/test/single_page_crawl_upsert.py",
        URL
    ])

# ✅ Schedule to run every 2 minutes
schedule.every(2).minutes.do(job)

print("⏰ Scheduler started. Will crawl & upsert every 2 minutes for your product page.")

job()  # First immediate run

while True:
    schedule.run_pending()
    time.sleep(1)
