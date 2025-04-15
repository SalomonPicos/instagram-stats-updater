# Dockerfile
FROM python:3.11-slim

# Install system libraries required by Playwright
RUN apt-get update && apt-get install -y \
    curl wget unzip gnupg2 \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libasound2 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 \
    libxdamage1 libxfixes3 libxext6 libx11-6 libx11-xcb1 libxcb1 \
    libxrender1 libxi6 libxtst6 libgbm1 libgtk-3-0 libpangocairo-1.0-0 \
    libpangoft2-1.0-0 libgraphite2-3 libharfbuzz0b libgdk-pixbuf2.0-0 \
    libgl1-mesa-glx libegl1-mesa \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install playwright and its dependencies
RUN playwright install --with-deps

# Copy code
COPY . .

# Default command
CMD ["python", "fetch_tiktok.py"]
