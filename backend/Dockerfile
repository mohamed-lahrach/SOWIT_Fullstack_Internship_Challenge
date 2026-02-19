# 1. Base Image: Start with a lightweight Linux + Python 3.10
FROM python:3.10-slim

# 2. Environment Variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures logs appear immediately in the console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Work Directory: Create a folder inside the container
WORKDIR /app

# 4. System Dependencies (The "Hard Part" made easy)
# We need these for GeoDjango (PostGIS support)
# gdal-bin + libgdal-dev → the C engine that does the spatial math
# python3-gdal           → system-level bindings (needed as base)
RUN apt-get update && apt-get install -y \
    build-essential \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*
# build-essential → g++, gcc, make (required to compile GDAL Python bindings)
# gdal-bin + libgdal-dev → the GDAL C engine and headers
# libproj-dev → projection library for coordinate systems
# python3-gdal → system-level GDAL bindings used as base

# 4.5 Fix: Install GDAL Python bindings into the correct Python (pip's Python)
# We match the version exactly to what apt-get installed
# Without this step → "from osgeo import gdal" fails with ModuleNotFoundError
RUN pip install --no-cache-dir GDAL==$(gdal-config --version)

# 5. Install Python Dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Project Code
# We copy the rest of the code last to speed up rebuilds
COPY . /app/

# 7. Default Command
# This runs the development server accessible from outside the container
# Copy entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# This is the magic line
ENTRYPOINT ["/entrypoint.sh"]