# LCM Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0+-00a393.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed.svg)](https://www.docker.com/)

A comprehensive framework for comparing and evaluating language models, with emphasis on Meta's Large Concept Model (LCM-7B) and Llama 3 models.

## 🌟 Features

- **🔄 Multi-model Support**: Compare LCM-7B and Llama 3 models head-to-head
- **📊 Comparative Metrics**: Analysis of speed, accuracy, reasoning, creativity, and hallucination risk
- **🖥️ Interactive UIs**: Multiple interfaces from basic chat to advanced comparison views
- **🧪 Comprehensive Testing**: Acceptance tests, stress tests, and predefined test cases
- **📈 Performance Monitoring**: Latency, GPU utilization, memory usage tracking

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/lcm-framework.git
cd lcm-framework

# Start all services
docker-compose up
```

### Manual Installation

#### Option 1: Using venv (Traditional)

```bash
# Clone the repository
git clone https://github.com/yourusername/lcm-framework.git
cd lcm-framework

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Download models (see Model Download section below)
python scripts/download_models.py
python scripts/download_lcm_from_github.py

# Start the application
python run.py
```

#### Option 2: Using uv (Recommended for faster installation)

```bash
# Clone the repository
git clone https://github.com/yourusername/lcm-framework.git
cd lcm-framework

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies with uv (much faster)
uv pip install -r requirements.txt

# Download models (see Model Download section below)
python scripts/download_models.py
python scripts/download_lcm_from_github.py

# Start the application
python run.py
```

## 🏗️ Project Structure

```
lcm/
├── src/                  # Source code
│   ├── api/              # FastAPI backend
│   ├── inference/        # Model inference 
│   ├── ui/               # User interfaces
│   ├── comparison/       # Model comparison
│   └── utils/            # Utilities
├── tests/                # Test files
├── docs/                 # Documentation
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── data/                 # Data storage
└── ...
```

## 🖥️ Usage

### Running the API Server

```bash
python run.py --api
```

### Running the Chat UI

```bash
python run.py --ui
```

### Running the Comparison UI

```bash
python run.py --ui --comparison
```

### Command Line Options

- `--host`: Host to run on (default: 0.0.0.0)
- `--port`: Port to run on (default: 8000)
- `--reload`: Enable auto-reload for development
- `--ui`: Run UI only
- `--api`: Run API only
- `--comparison`: Run in comparison mode

## 📥 Model Download

The framework requires two models:

### 1. Llama 3 8B from Hugging Face

```bash
# Activate your virtual environment first
source venv/bin/activate  # or .venv/bin/activate if using uv

# Download Llama 3 8B
python scripts/download_models.py
```

**Important**: Before running this script, you must:
1. Have a Hugging Face account
2. Visit https://huggingface.co/meta-llama/Meta-Llama-3-8B
3. Accept Meta's license terms
4. Log in via `huggingface-cli login` when prompted

### 2. LCM Setup from Meta's GitHub Repository

```bash
# Activate your virtual environment first
source venv/bin/activate  # or .venv/bin/activate if using uv

# Set up LCM environment
python scripts/download_lcm_from_github.py
```

This script will:
1. Clone Meta's large_concept_model and SONAR repositories
2. Set up the environment for LCM
3. Create documentation in the `models/lcm` directory

**Important Note**: Meta's GitHub repository does not provide pre-trained LCM models for direct download. Instead, it provides code to train and fine-tune LCM models from scratch. The SONAR models (used for embeddings) will be automatically downloaded when using the library.

**Hardware Requirements**:
- Storage: At least 10GB free space for repositories and SONAR models
- Memory: 16GB+ RAM
- GPU: 24GB+ VRAM recommended if you decide to train your own LCM model

## 📊 Using SONAR Embeddings Directly

Since pre-trained LCM models are not available for direct download, you can use SONAR embeddings directly for various NLP tasks. SONAR provides a powerful multilingual and multimodal embedding space that can be used for:

- Semantic similarity comparison
- Cross-lingual document retrieval
- Text clustering and classification
- And more

We've provided a comprehensive guide on using SONAR embeddings:

**[📚 Detailed Guide: Using SONAR Embeddings](docs/using_sonar_embeddings.md)**

This guide includes:
- Installation instructions for SONAR and its dependencies
- Code examples for encoding sentences and computing similarity
- Advanced usage with multilingual support
- Text reconstruction capabilities
- Integration ideas for the LCM Framework

SONAR models will be automatically downloaded when using the library.

## 📊 Model Comparison

The framework provides comprehensive comparison between models across multiple dimensions:

| Metric | Description |
|--------|-------------|
| Speed | Processing time and tokens per second |
| Accuracy | Correctness on factual questions |
| Reasoning | Logical consistency and problem-solving |
| Creativity | Originality and diversity of responses |
| Hallucination | Risk of generating false information |

## 🧪 Testing

```bash
# Run acceptance tests
pytest tests/acceptance

# Run stress tests
pytest tests/stress

# Run all tests
pytest
```

## 🔧 Configuration

Configuration is managed through environment variables and the `config/settings.py` file:

```python
# Example configuration override
export API_HOST=localhost
export API_PORT=8080
export USE_GPU=True
```

## 📚 Documentation

- API documentation is available at `http://localhost:8000/docs`
- Additional guides are in the `docs/` directory

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Meta AI](https://ai.meta.com/) for the LCM and Llama models
- [Hugging Face](https://huggingface.co/) for model hosting and Transformers library
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Gradio](https://gradio.app/) for the UI components
