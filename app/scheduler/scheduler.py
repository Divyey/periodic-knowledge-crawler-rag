# app/scheduler/scheduler.py
import os
import subprocess
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

logfile = os.path.join(os.path.dirname(__file__), "../../logs/scheduler.log")
os.makedirs(os.path.dirname(logfile), exist_ok=True)
file_handler = logging.FileHandler(logfile)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
logging.getLogger().addHandler(file_handler)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"[SCHEDULER] PROJECT_ROOT = {PROJECT_ROOT}")

def run_pipeline():
    logging.info("Starting crawl and upsert pipeline...")
    try:
        subprocess.run(["python", "-m", "app.crawler.crawler_mp"], check=True, cwd=PROJECT_ROOT)
        subprocess.run(["python", "-m", "app.upsert.upsert"], check=True, cwd=PROJECT_ROOT)

        logging.info("Pipeline run complete.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, "interval", minutes=20, max_instances=1, coalesce=True)
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    run_pipeline()
    scheduler.start()

# python -m app.scheduler.scheduler
# streamlit run app/chatbot/chatbot.py
