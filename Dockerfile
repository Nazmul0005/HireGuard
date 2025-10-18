FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install required packages and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    musl-dev \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code into the container
COPY . /app/

# Expose port 8000 (Uvicorn will run here)
EXPOSE 8000

# Run the Uvicorn server
CMD ["uvicorn", "com.mhire.app.main:app", "--host", "0.0.0.0", "--port", "8000"]