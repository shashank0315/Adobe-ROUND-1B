FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy backend code
COPY backend/ ./backend/

# Copy frontend package files
COPY frontend/package*.json ./frontend/
COPY frontend/yarn.lock ./frontend/

# Install frontend dependencies
WORKDIR /app/frontend
RUN npm install

# Copy frontend source code
COPY frontend/src/ ./src/
COPY frontend/public/ ./public/
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./
COPY frontend/craco.config.js ./

# Build frontend
RUN npm run build

# Copy challenge data
WORKDIR /app
COPY challenge_data/ ./challenge_data/

# Copy test files
COPY backend_test.py ./
COPY comprehensive_test.py ./
COPY test_result.md ./

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Default command to run the backend server
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"] 