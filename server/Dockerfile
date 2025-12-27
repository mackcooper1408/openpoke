FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for building some python packages)
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server package
COPY server/ ./server/

# Expose the port
EXPOSE 8001

# Run the server
CMD ["python", "-m", "server.server", "--host", "0.0.0.0", "--port", "8001"]
