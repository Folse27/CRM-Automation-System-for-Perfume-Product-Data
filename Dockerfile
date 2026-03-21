FROM mcr.microsoft.com/playwright/python:v1.58.0

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

# (Optional) ensure env file path exists
RUN mkdir -p /etc/secrets

# Start your bot
CMD ["python", "product_data_enricher.py"]
