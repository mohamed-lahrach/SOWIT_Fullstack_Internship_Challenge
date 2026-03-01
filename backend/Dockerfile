FROM python:3.10-slim

# Two lines. Both are standard in every professional Django Dockerfile.
# Python, don't write bytecode
ENV PYTHONDONTWRITEBYTECODE=1
# Python, unbuffered
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System Dependencies
RUN apt-get update && apt-get install -y \
    #the compilers (gcc, g++, make)
    build-essential \
    # the linker (ld)
    binutils \
    #(SRID 4326  →  PROJ  →  SRID 32629) => (degrees -> PROJ transform -> meters)
    # coordinate math library GDAL depends on
    libproj-dev \ 
    #  GDAL command line tools (gdal-config --version)
    gdal-bin \
    #  GDAL C Headers The .h header files that define all GDAL's C functions
    libgdal-dev \
    # The base layer of Python-to-GDAL communication at the system level (able to run pip commands) redundant line(installed in the wrong house)
    # python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Fix GDAL Python bindings (installed in the right house)
# Django only looks in one house — pip's house.
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