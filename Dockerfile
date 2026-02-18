# Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 perfsonar && \
    chown -R perfsonar:perfsonar /app

USER perfsonar

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port if needed for future HTTP transport
EXPOSE 8000

# Default command
CMD ["fastmcp", "run", "src/perfsonar_mcp/fastmcp_server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
