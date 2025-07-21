FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for Chrome/Chromedriver)
RUN apt-get update && \
    apt-get install -y wget curl unzip fonts-liberation libasound2 libnspr4 libnss3 libxss1 libxtst6 libatk-bridge2.0-0 libgtk-3-0 libgbm1 chromium chromium-driver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Set environment variables (example)
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.scheduler.scheduler"]
