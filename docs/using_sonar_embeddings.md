# Using SONAR Embeddings Directly

Since pre-trained LCM models are not available for direct download, you can use SONAR embeddings directly for various NLP tasks. This guide explains how to set up and use SONAR embeddings in your projects.

## What is SONAR?

SONAR (Sentence-level multimOdal and laNguage-Agnostic Representations) is a multilingual and multimodal fixed-size sentence embedding space developed by Meta. It provides powerful embeddings that can be used for:

- Semantic similarity comparison
- Cross-lingual document retrieval
- Text clustering and classification
- And more

SONAR supports up to 200 languages in text and 57 languages in speech.

## Installation

SONAR requires specific versions of fairseq2 that match your PyTorch and CUDA versions. Follow these steps to install it correctly:

```bash
# 1. Activate your virtual environment
source venv/bin/activate  # or .venv/bin/activate if using uv

# 2. Check your PyTorch version
python -c "import torch; print(torch.__version__)"
# Example output: 2.7.0

# 3. Install fairseq2 with the matching PyTorch version
# Replace X.Y.Z with your PyTorch version (e.g., 2.6.0)
# Replace cuda/cpu with your compute platform
pip install fairseq2==0.4.5 --extra-index-url https://fair.pkg.atmeta.com/fairseq2/whl/ptX.Y.Z/cuda

# 4. Install SONAR
pip install sonar-space
```

If fairseq2 doesn't provide a pre-built package for your specific PyTorch version, you may need to build it from source. Refer to the [fairseq2 repository](https://github.com/facebookresearch/fairseq2) for instructions.

## Using SONAR Embeddings

Here's a complete example of how to use SONAR embeddings for semantic similarity:

```python
import torch
import numpy as np
from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline

# Function to compute cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Initialize the SONAR text encoder
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

t2vec_model = TextToEmbeddingModelPipeline(
    encoder="text_sonar_basic_encoder",
    tokenizer="text_sonar_basic_encoder",
    device=device,
    dtype=dtype
)

# Example sentences
sentences = [
    "The Large Concept Model (LCM) operates on an explicit higher-level semantic representation.",
    "LCM uses the SONAR embedding space, which supports up to 200 languages in text.",
    "Llama 3 is a large language model developed by Meta.",
    "The LCM Framework provides tools for comparing language models."
]

# Encode sentences into the SONAR embedding space
embeddings = t2vec_model.predict(sentences, source_lang="eng_Latn")
print(f"Embeddings shape: {embeddings.shape}")  # Should be [4, 1024]

# Convert to numpy for easier manipulation
embeddings_np = embeddings.cpu().numpy()

# Compute similarity matrix
similarity_matrix = np.zeros((len(sentences), len(sentences)))
for i in range(len(sentences)):
    for j in range(len(sentences)):
        similarity_matrix[i, j] = cosine_similarity(embeddings_np[i], embeddings_np[j])

# Print similarity matrix
print("Similarity matrix:")
for i, sentence in enumerate(sentences):
    print(f"Sentence {i+1}: {sentence[:50]}...")

print("\nSimilarity Matrix:")
for i in range(len(sentences)):
    similarity_row = " ".join([f"{similarity_matrix[i, j]:.4f}" for j in range(len(sentences))])
    print(f"Sentence {i+1}: {similarity_row}")
```

## Advanced Usage

### Multilingual Support

SONAR supports over 200 languages. To use a different language, simply specify the language code:

```python
# Spanish example
spanish_sentences = [
    "SONAR es un modelo de incrustación multilingüe.",
    "Puede procesar texto en más de 200 idiomas."
]

# Use the ISO 639-3 language code with script
embeddings = t2vec_model.predict(spanish_sentences, source_lang="spa_Latn")
```

### Text Reconstruction

SONAR also provides a decoder to reconstruct text from embeddings:

```python
from sonar.inference_pipelines.text import EmbeddingToTextModelPipeline

# Initialize the decoder
vec2t_model = EmbeddingToTextModelPipeline(
    decoder="text_sonar_basic_decoder",
    device=device,
    dtype=dtype
)

# Reconstruct text from embeddings
reconstructed_texts = vec2t_model.predict(
    embeddings,
    target_lang="eng_Latn",
    beam_size=5
)

for original, reconstructed in zip(sentences, reconstructed_texts):
    print(f"Original: {original}")
    print(f"Reconstructed: {reconstructed}")
    print()
```

## Integration with LCM Framework

You can integrate SONAR embeddings into the LCM Framework for various tasks:

1. **Semantic Search**: Use SONAR embeddings to find semantically similar documents
2. **Cross-lingual Comparison**: Compare texts across different languages
3. **Document Clustering**: Group similar documents together
4. **Text Classification**: Classify texts based on their semantic content

## Resources

- [SONAR GitHub Repository](https://github.com/facebookresearch/SONAR)
- [SONAR Paper](https://ai.meta.com/research/publications/sonar-sentence-level-multimodal-and-language-agnostic-representations/)
- [fairseq2 GitHub Repository](https://github.com/facebookresearch/fairseq2)