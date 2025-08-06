# Use an official Python image as a base
FROM python:3.11-slim

# Install system dependencies for Chromium and Selenium
RUN apt-get update && \
    apt-get install -y wget gnupg2 && \
    apt-get install -y chromium chromium-driver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port (change if needed)
EXPOSE 10000

# Start the app with Uvicorn
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
