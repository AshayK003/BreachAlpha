# ── Build stage: compile React frontend ──────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Runtime stage: Python + built frontend ──────────────────────────
FROM python:3.12-slim
WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY breachalpha/ ./breachalpha/
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy pre-built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "breachalpha.server:app", "--host", "0.0.0.0", "--port", "8000"]
