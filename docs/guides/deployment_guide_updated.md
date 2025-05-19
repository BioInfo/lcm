# Meta LCM Chatbot Deployment Guide (Updated with Comparison Feature)

This guide provides comprehensive instructions for deploying the Meta LCM Chatbot with the new model comparison feature, allowing you to compare LCM-7B (concept-level reasoning) with Llama-7B (token-level processing).

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Options](#installation-options)
3. [Docker Deployment (Recommended)](#docker-deployment-recommended)
4. [Manual Installation](#manual-installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Comparison Feature Setup](#comparison-feature-setup)
8. [Troubleshooting](#troubleshooting)
9. [Updating](#updating)

## System Requirements

### Minimum Requirements
- **CPU**: 4+ cores
- **RAM**: 16GB
- **Storage**: 20GB free space
- **GPU**: NVIDIA GPU with 24GB+ VRAM (for optimal performance)
- **OS**: macOS, Linux, or Windows with WSL2

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 50GB SSD
- **GPU**: NVIDIA GPU with 32GB+ VRAM
- **OS**: Ubuntu 20.04+ or macOS 12+

### CPU-Only Mode
- The application can run in CPU-only mode with reduced performance (3+ second latency)
- Requires 32GB+ RAM for CPU-only operation

## Installation Options

You can deploy the Meta LCM Chatbot in two ways:

1. **Docker Deployment (Recommended)**: Easier setup with containerized environment
2. **Manual Installation**: Direct installation on your local machine

## Docker Deployment (Recommended)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for GPU support)

### Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/meta/lcm-chatbot.git
   cd lcm-chatbot
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file to set:
   - `ENABLE_GPU=true` (or `false` for CPU-only mode)
   - `MODEL_CACHE_DIR=/path/to/model/cache` (optional, for persistent model storage)
   - `ENABLE_COMPARISON=true` (to enable the comparison feature)

3. **Build and start the containers**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   
   The application should now be running at:
   - Web UI: http://localhost:7860
   - API: http://localhost:8000/api/health

## Manual Installation

### Prerequisites
- Python 3.9+
- [PyTorch](https://pytorch.org/get-started/locally/) with CUDA support (for GPU acceleration)
- Redis 6.0+

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/meta/lcm-chatbot.git
   cd lcm-chatbot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install additional comparison feature dependencies**
   ```bash
   pip install -r requirements-comparison.txt
   ```

5. **Download models**
   ```bash
   python app/utils/download_models.py
   ```

6. **Start Redis server**
   ```bash
   # Install Redis if not already installed
   # Ubuntu: sudo apt install redis-server
   # macOS: brew install redis
   
   # Start Redis server
   redis-server --daemonize yes
   ```

7. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file to set:
   - `ENABLE_GPU=true` (or `false` for CPU-only mode)
   - `REDIS_URL=redis://localhost:6379/0`
   - `ENABLE_COMPARISON=true` (to enable the comparison feature)

## Configuration

### Core Configuration Options

Edit the `.env` file to customize your deployment:

| Option | Description | Default |
|--------|-------------|---------|
| `PORT` | Web UI port | 7860 |
| `API_PORT` | API port | 8000 |
| `ENABLE_GPU` | Enable GPU acceleration | true |
| `MAX_MEMORY` | Maximum memory usage (MB) | 24000 |
| `REDIS_URL` | Redis connection URL | redis://redis:6379/0 |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | INFO |
| `ENABLE_COMPARISON` | Enable model comparison feature | true |

### Comparison Feature Configuration

Additional options for the comparison feature:

| Option | Description | Default |
|--------|-------------|---------|
| `COMPARISON_MODE` | Default comparison mode (interactive, batch) | interactive |
| `LCM_MODEL_PATH` | Path to LCM-7B model | models/lcm-7b |
| `LLAMA_MODEL_PATH` | Path to Llama-7B model | models/llama-7b |
| `ENABLE_MULTIMODAL` | Enable multimodal comparison | true |
| `ENABLE_CROSS_LINGUAL` | Enable cross-lingual comparison | true |
| `METRICS_LOG_DIR` | Directory for metrics logging | app/data/logs |

## Running the Application

### Using Docker

The application starts automatically after `docker-compose up -d`. To restart or stop:

```bash
# Restart services
docker-compose restart

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Manual Execution

1. **Start the API server**
   ```bash
   cd lcm-chatbot
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python app/main.py
   ```

2. **In a new terminal, start the UI**
   ```bash
   cd lcm-chatbot
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python app/ui/chat_ui.py  # For standard UI
   # OR
   python app/ui/head_to_head_ui.py  # For comparison UI
   ```

3. **Access the application**
   - Standard UI: http://localhost:7860
   - Comparison UI: http://localhost:7861

## Comparison Feature Setup

The comparison feature requires both LCM-7B and Llama-7B models. Here's how to set it up:

### Automatic Setup

The `download_models.py` script automatically downloads both models:

```bash
python app/utils/download_models.py --download-all
```

### Manual Model Setup

If you prefer to download models manually:

1. **Download LCM-7B**
   ```bash
   python app/utils/download_models.py --model lcm
   ```

2. **Download Llama-7B**
   ```bash
   python app/utils/download_models.py --model llama
   ```

3. **Verify models**
   ```bash
   python app/utils/verify_models.py
   ```

### Testing the Comparison Feature

1. **Run acceptance tests**
   ```bash
   python app/utils/acceptance_tests_comparison.py
   ```

2. **Try interactive comparison**
   - Access the comparison UI at http://localhost:7861
   - Enter a prompt and click "Compare Models"
   - View the side-by-side results and metrics

## Troubleshooting

### Common Issues

#### GPU Memory Errors
- **Symptom**: "CUDA out of memory" errors
- **Solution**: 
  - Reduce `MAX_MEMORY` in `.env`
  - Set `ENABLE_GPU=false` to use CPU mode

#### Model Download Failures
- **Symptom**: Model download errors or timeouts
- **Solution**:
  - Check internet connection
  - Try manual download with `--resume` flag:
    ```bash
    python app/utils/download_models.py --model llama --resume
    ```

#### Redis Connection Issues
- **Symptom**: "Cannot connect to Redis" errors
- **Solution**:
  - Verify Redis is running: `redis-cli ping`
  - Check `REDIS_URL` in `.env`

#### Comparison Feature Not Working
- **Symptom**: Comparison feature unavailable or errors
- **Solution**:
  - Verify both models are downloaded
  - Check `ENABLE_COMPARISON=true` in `.env`
  - Run `python app/utils/verify_models.py`

### Logs

Check logs for detailed error information:

- **Docker**: `docker-compose logs -f`
- **Manual**: Check console output or `app/data/logs/`

## Updating

### Docker Update

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Manual Update

```bash
git pull
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-comparison.txt
python app/utils/download_models.py --update
```

## Additional Resources

- [Demo Guide](demo_guide.md)
- [Comparison Feature Demo Guide](demo_guide_comparison.md)
- [API Documentation](api_docs.md)
- [Feedback Form](comparison_feedback_form.md)

## Support

For issues or questions, please contact:
- Email: lcm-support@meta.ai
- GitHub Issues: https://github.com/meta/lcm-chatbot/issues
