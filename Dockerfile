# Aschenpfad – Spiel + Mehrspieler-Server in einem Container
FROM node:22-alpine
WORKDIR /app
COPY server/server.js ./server.js
COPY index.html ./index.html
ENV PORT=8080
EXPOSE 8080
CMD ["node", "server.js"]
