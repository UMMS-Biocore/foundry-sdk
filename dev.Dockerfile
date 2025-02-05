# Use Python 3.8 as base image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

#############################
# Install system dependencies
#############################
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --no-cache-dir -U pip setuptools wheel

# Create a non-root user
RUN useradd -m -s /bin/bash developer

# Copy the SDK files
COPY --chown=developer:developer . .

# Install the package in editable mode with development dependencies
RUN pip install --no-cache-dir -e ".[dev]"

###########################
# Set environment variables
###########################
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Prevent .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Enable fault handler for easier debugging
ENV PYTHONFAULTHANDLER=1


###########################
# Set default user
###########################
USER developer

# Default command to run an interactive shell
CMD ["/bin/bash"]
