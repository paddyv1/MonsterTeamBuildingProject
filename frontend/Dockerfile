FROM node:20-alpine

WORKDIR /app

# Install deps first (cache-friendly)
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* /app/
RUN npm install

# Copy source
COPY . /app

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]