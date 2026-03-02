# Frontend Dockerfile (Development)
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source code
COPY frontend/ .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
