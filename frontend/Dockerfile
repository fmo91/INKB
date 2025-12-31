FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 19006

CMD ["npm", "run", "web", "--", "--host", "lan", "--port", "19006"]
