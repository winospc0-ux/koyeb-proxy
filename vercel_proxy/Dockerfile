FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port (Koyeb will set $PORT, defaulting to 8000)
EXPOSE 8000

# Ensure logs are printed immediately
ENV PYTHONUNBUFFERED=1

# Run the app with gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 api.index:app"]
