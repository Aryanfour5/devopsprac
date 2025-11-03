# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Install Python and pip for testing
RUN apk add --no-cache python3 py3-pip

COPY --from=builder /app/node_modules ./node_modules
COPY . .

# Copy test requirements
COPY requirements-test.txt .

# Install Python test dependencies
RUN pip3 install --no-cache-dir -r requirements-test.txt

EXPOSE 3000

CMD ["node", "app.js"]
