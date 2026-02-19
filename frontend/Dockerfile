FROM node:20-alpine
WORKDIR /app
RUN npm install -g create-vite   # ← available instantly, no npx download wait
EXPOSE 5173
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]