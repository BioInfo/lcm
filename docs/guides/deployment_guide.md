# Meta LCM Chatbot Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the Meta LCM Chatbot on your local MacBook. The application can be deployed using either Docker (recommended) or manual installation.

## Prerequisites

- MacBook with macOS 11.0+ (Big Sur or newer)
- At least 8GB RAM (16GB recommended)
- At least 10GB free disk space
- Internet connection for downloading models

## Option 1: Docker Deployment (Recommended)

### Requirements

- [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) installed
- [Git](https://git-scm.com/download/mac) installed

### Deployment Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/meta-lcm-chatbot.git
   cd meta-lcm-chatbot
   ```

2. **Build and start the application**:
   ```bash
   docker-compose up --build
   ```
   This will:
   - Build the Docker image
   - Download required models
   - Start the application and Redis server

3. **Access the application**:
   - Open your browser and navigate to: http://localhost:8000
   - The API documentation is available at: http://localhost:8000/docs
   - The health endpoint is available at: http://localhost:8000/health

4. **Stop the application**:
   ```bash
   # Press Ctrl+C in the terminal where docker-compose is running
   # Or run in a new terminal:
   docker-compose down
   ```

### Troubleshooting Docker Deployment

- **Issue**: Container fails to start
  - **Solution**: Check Docker logs with `docker-compose logs`

- **Issue**: Models fail to download
  - **Solution**: Run `docker-compose down -v` to remove volumes and try again

- **Issue**: Application is slow
  - **Solution**: Enable GPU support in Docker Desktop settings if available

## Option 2: Manual Installation

### Requirements

- Python 3.11+ installed
- [Homebrew](https://brew.sh/) installed (for Redis)
- [Git](https://git-scm.com/download/mac) installed

### Deployment Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/meta-lcm-chatbot.git
   cd meta-lcm-chatbot
   ```

2. **Install Redis**:
   ```bash
   brew install redis
   brew services start redis
   ```

3. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download models**:
   ```bash
   python app/utils/download_models.py
   ```
   Note: This may take some time depending on your internet connection.

5. **Start the application**:
   ```bash
   python app/main.py
   ```

6. **Access the application**:
   - Open your browser and navigate to: http://localhost:8000
   - The API documentation is available at: http://localhost:8000/docs
   - The health endpoint is available at: http://localhost:8000/health

7. **Stop the application**:
   ```bash
   # Press Ctrl+C in the terminal where the application is running
   # To stop Redis:
   brew services stop redis
   ```

### Troubleshooting Manual Installation

- **Issue**: Package installation fails
  - **Solution**: Try `pip install --no-cache-dir -r requirements.txt`

- **Issue**: Redis connection error
  - **Solution**: Verify Redis is running with `brew services list`

- **Issue**: Models fail to download
  - **Solution**: Try downloading manually from the model repositories

## Configuration Options

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port to run the application | 8000 |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `MODEL_PATH` | Path to model directory | app/models |
| `LOG_LEVEL` | Logging level | INFO |

Example:
```bash
# For Docker:
PORT=9000 docker-compose up

# For manual installation:
export PORT=9000
python app/main.py
```

## API Usage

The chatbot provides a REST API for integration with other applications:

### Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "session_id": "optional-session-id"}'
```

### Clear History Endpoint

```bash
curl -X POST http://localhost:8000/api/clear-history?session_id=your-session-id
```

### Health Endpoint

```bash
curl http://localhost:8000/health
```

## Performance Considerations

- **CPU Mode**: If no GPU is available, the application will run in CPU-only mode with increased latency (≥ 3s)
- **Memory Usage**: The application requires approximately 4GB of RAM in CPU mode and 2GB + VRAM in GPU mode
- **Disk Space**: Models require approximately 5GB of disk space

## Security Notes

- This MVP is intended for local deployment and demonstration purposes only
- No authentication is implemented
- No PII is stored in the application
- For production deployment, additional security measures would be required

## Updating the Application

To update the application to the latest version:

```bash
# For Docker:
git pull
docker-compose down
docker-compose up --build

# For manual installation:
git pull
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

---

For additional support or questions, please contact the development team.
