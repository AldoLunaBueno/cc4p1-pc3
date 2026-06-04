FROM node:20-bookworm-slim

WORKDIR /app

# Copiamos el package.json e instalamos dependencias
COPY package*.json ./
RUN npm install

COPY index.js .

CMD ["node", "index.js"]