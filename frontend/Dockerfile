FROM node:20-alpine

WORKDIR /app

# 1. Install global tools for scaffolding
RUN npm install -g create-vite

# 2. Copy ONLY the entrypoint (Crucial: Do not copy . /app)
COPY entrypoint.sh /entrypoint.sh

# 3. Permissions & Cleanup
RUN chmod +x /entrypoint.sh && \
    sed -i 's/\r$//' /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]