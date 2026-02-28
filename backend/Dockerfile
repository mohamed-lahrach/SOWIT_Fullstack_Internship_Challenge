FROM python:3.10-slim

# Two lines. Both are standard in every professional Django Dockerfile.
# Python, don't write bytecode
ENV PYTHONDONTWRITEBYTECODE=1
# Python, unbuffered
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Fix GDAL Python bindings
RUN pip install --no-cache-dir GDAL==$(gdal-config --version)

#Install Python Dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# --- THE FIX IS HERE ---
# We explicitly copy the entrypoint to the ROOT of the image
COPY entrypoint.sh /entrypoint.sh

# We fix permissions and line endings (crucial for Mac/Linux compatibility)
RUN chmod +x /entrypoint.sh && \
    sed -i 's/\r$//' /entrypoint.sh

#Define the Entrypoint
ENTRYPOINT ["/entrypoint.sh"]