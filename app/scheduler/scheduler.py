import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from app.crawler.crawler_mp import main as crawl_main
from app.upsert.upsert import upsert_chunks_optimal

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
        chunks = crawl_main()
        logging.info(f"Crawled {len(chunks)} chunks, starting upsert...")
        upsert_chunks_optimal(chunks)
        logging.info("Pipeline run complete.")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")


# if __name__ == "__main__":
#     scheduler = BlockingScheduler()
#     scheduler.add_job(run_pipeline, "interval", minutes=30, max_instances=1, coalesce=True)
#     logging.info("Scheduler started. Press Ctrl+C to exit.")
#     run_pipeline()
#     scheduler.start()
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, "interval", minutes=30, max_instances=1, coalesce=True)
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    run_pipeline()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler is shutting down gracefully...")
        scheduler.shutdown()

# python -m app.scheduler.scheduler
# streamlit run app/chatbot/chatbot.py
